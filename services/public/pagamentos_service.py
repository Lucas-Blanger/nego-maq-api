from database import db
from database.models import (
    Pedido,
    TransacaoPagamento,
    StatusPagamentoEnum,
    StatusPedidoEnum,
)
from services.public.mercadopago_service import MercadoPagoService


class PagamentoService:

    @staticmethod
    def criar_preferencia_pagamento(pedido_id):
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            raise ValueError("Pedido não encontrado")

        # Preparar itens com informações dos produtos
        itens = []
        for item in pedido.itens:
            itens.append(
                {
                    "produto_id": item.produto_id,
                    "nome": item.produto.nome,
                    "descricao": item.produto.descricao,
                    "img": item.produto.img,
                    "categoria": item.produto.categoria,
                    "quantidade": item.quantidade,
                    "preco_unitario": item.preco_unitario,
                }
            )

        # Criar preferência no Mercado Pago
        mp_service = MercadoPagoService()
        preferencia = mp_service.criar_preferencia_pagamento(pedido, itens)

        # Criar transação pendente
        transacao = TransacaoPagamento(
            pedido_id=pedido.id,
            valor=pedido.valor_total,
            metodo_pagamento="mercadopago",
            status=StatusPagamentoEnum.PENDENTE,
            mp_preference_id=preferencia["preference_id"],
        )
        db.session.add(transacao)
        db.session.commit()

        return {
            "transacao_id": transacao.id,
            "pedido_id": pedido.id,
            "preference_id": preferencia["preference_id"],
            "checkout_url": preferencia["init_point"],
            "sandbox_checkout_url": preferencia["sandbox_init_point"],
        }

    @staticmethod
    def processar_webhook_mercadopago(data):
        """
        Processa notificações do webhook do Mercado Pago.
        Atualiza status da transação e do pedido automaticamente.
        """
        mp_service = MercadoPagoService()
        webhook_info = mp_service.processar_webhook(data)

        if not webhook_info:
            return None

        # Aceitar tanto merchant_order quanto payment
        payment_id = webhook_info.get("payment_id")

        if not payment_id:
            print("[PagamentoService] Webhook sem payment_id, ignorando")
            return None

        # Buscar transação pelo payment_id do MP
        transacao = TransacaoPagamento.query.filter_by(
            mp_payment_id=str(payment_id)
        ).first()

        if not transacao:
            # Buscar pelo pedido_id (external_reference)
            pedido_id = webhook_info.get("pedido_id")
            if pedido_id:
                transacao = (
                    TransacaoPagamento.query.filter_by(pedido_id=pedido_id)
                    .order_by(TransacaoPagamento.criado_em.desc())
                    .first()
                )

        if not transacao:
            print(
                f"[PagamentoService] Transação não encontrada para payment_id: {payment_id}"
            )
            pedido_id = webhook_info.get("pedido_id")
            if pedido_id:
                transacao = (
                    TransacaoPagamento.query.filter_by(pedido_id=pedido_id)
                    .order_by(TransacaoPagamento.criado_em.desc())
                    .first()
                )
                if transacao:
                    transacao.mp_payment_id = str(payment_id)

        if not transacao:
            raise ValueError("Transação não encontrada")

        status_map = {
            "approved": StatusPagamentoEnum.APROVADO,
            "pending": StatusPagamentoEnum.PENDENTE,
            "in_process": StatusPagamentoEnum.PENDENTE,
            "rejected": StatusPagamentoEnum.REJEITADO,
            "cancelled": StatusPagamentoEnum.CANCELADO,
            "refunded": StatusPagamentoEnum.REEMBOLSADO,
            "charged_back": StatusPagamentoEnum.REEMBOLSADO,
        }

        status_anterior = transacao.status
        novo_status = status_map.get(
            webhook_info["status"], StatusPagamentoEnum.PENDENTE
        )

        # Atualizar transação
        transacao.status = novo_status
        if not transacao.mp_payment_id:
            transacao.mp_payment_id = str(payment_id)

        # Atualizar pedido
        pedido = transacao.pedido
        if novo_status == StatusPagamentoEnum.APROVADO:
            pedido.status = StatusPedidoEnum.PAGO
            print(f"[PagamentoService] Pedido {pedido.id} marcado como PAGO")

            # Envia para o melhor invio
            try:
                from services.public.melhor_envio_service import (
                    criar_pedido_melhor_envio,
                    comprar_envio,
                    gerar_etiqueta,
                    imprimir_etiqueta,
                )

                print(f"[MELHOR ENVIO] Iniciando envio do pedido {pedido.id}")

                # 1. Criar pedido no Melhor Envio
                resultado_me = criar_pedido_melhor_envio(pedido)
                pedido.melhor_envio_id = resultado_me.get("melhor_envio_id")
                pedido.melhor_envio_protocolo = resultado_me.get("protocol")
                print(f"[MELHOR ENVIO] Pedido criado: {pedido.melhor_envio_id}")

                # 2. Comprar o frete
                comprar_envio(pedido.melhor_envio_id)
                print(f"[MELHOR ENVIO] Frete comprado")

                # 3. Gerar etiqueta
                gerar_etiqueta(pedido.melhor_envio_id)
                print(f"[MELHOR ENVIO] Etiqueta gerada")

                # 4. Obter link da etiqueta
                etiqueta_url = imprimir_etiqueta(pedido.melhor_envio_id)
                pedido.etiqueta_url = etiqueta_url
                print(f"[MELHOR ENVIO] Etiqueta disponível: {etiqueta_url}")

                # 5. Atualizar status para EM_SEPARACAO
                pedido.status = StatusPedidoEnum.EM_SEPARACAO
                print(f"[MELHOR ENVIO] Processo concluído com sucesso!")

            except Exception as e:
                print(f"[MELHOR ENVIO] ERRO ao processar envio: {str(e)}")
                # Não vamos falhar o pagamento por causa do envio
                # O pedido fica como PAGO e pode ser enviado manualmente depois

        elif novo_status == StatusPagamentoEnum.REJEITADO:
            pedido.status = StatusPedidoEnum.CANCELADO
            print(
                f"[PagamentoService] Pedido {pedido.id} marcado como CANCELADO (rejeitado)"
            )
        elif novo_status == StatusPagamentoEnum.REEMBOLSADO:
            pedido.status = StatusPedidoEnum.CANCELADO
            PagamentoService._reverter_estoque(pedido)
            print(
                f"[PagamentoService] Pedido {pedido.id} estornado e estoque revertido"
            )

        db.session.commit()

        return {
            "transacao_id": transacao.id,
            "pedido_id": pedido.id,
            "status_anterior": status_anterior.value,
            "status_novo": novo_status.value,
            "pedido_status": pedido.status.value,
        }

    @staticmethod
    def _reverter_estoque(pedido):
        # Reverte o estoque dos produtos do pedido
        from database.models.produto import Produto

        for item in pedido.itens:
            produto = Produto.query.get(item.produto_id)
            if produto:
                produto.estoque += item.quantidade
                print(
                    f"[PagamentoService] Estoque revertido: {produto.nome} +{item.quantidade}"
                )

    @staticmethod
    def estornar_pagamento(transacao_id, valor=None):
        transacao = TransacaoPagamento.query.get(transacao_id)
        if not transacao:
            raise ValueError("Transação não encontrada")

        if not transacao.mp_payment_id:
            raise ValueError("Transação não possui payment_id do Mercado Pago")

        mp_service = MercadoPagoService()
        resultado = mp_service.estornar_pagamento(transacao.mp_payment_id, valor)

        # Atualizar status
        transacao.status = StatusPagamentoEnum.REEMBOLSADO
        transacao.pedido.status = StatusPedidoEnum.CANCELADO

        # Reverter estoque
        PagamentoService._reverter_estoque(transacao.pedido)

        db.session.commit()

        return {
            "refund_id": resultado["refund_id"],
            "transacao_id": transacao.id,
            "valor_estornado": resultado["amount"],
            "status": resultado["status"],
        }

    @staticmethod
    def listar_transacoes(pedido_id):
        # Lista todas as transações de um pedido
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            raise ValueError("Pedido não encontrado")
        return pedido.transacoes

    @staticmethod
    def consultar_transacao(transacao_id):
        # Consulta detalhes de uma transação específica
        transacao = TransacaoPagamento.query.get(transacao_id)
        if not transacao:
            raise ValueError("Transação não encontrada")

        if transacao.mp_payment_id:
            try:
                mp_service = MercadoPagoService()
                pagamento_mp = mp_service.consultar_pagamento(transacao.mp_payment_id)

                # Atualizar status se mudou
                status_map = {
                    "approved": StatusPagamentoEnum.APROVADO,
                    "pending": StatusPagamentoEnum.PENDENTE,
                    "in_process": StatusPagamentoEnum.PENDENTE,
                    "rejected": StatusPagamentoEnum.REJEITADO,
                    "cancelled": StatusPagamentoEnum.CANCELADO,
                    "refunded": StatusPagamentoEnum.REEMBOLSADO,
                    "charged_back": StatusPagamentoEnum.REEMBOLSADO,
                }

                novo_status = status_map.get(pagamento_mp["status"])
                if novo_status and novo_status != transacao.status:
                    transacao.status = novo_status
                    db.session.commit()

            except Exception as e:
                print(f"[PagamentoService] Erro ao consultar MP: {e}")

        return transacao
