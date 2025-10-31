from database import db
from database.models import (
    Pedido,
    TransacaoPagamento,
    StatusPagamentoEnum,
    StatusPedidoEnum,
)
from services.public.mercadopago_service import MercadoPagoService
from services.public.melhor_envio_service import (
    criar_pedido_melhor_envio,
    comprar_envio,
    gerar_etiqueta,
    imprimir_etiqueta,
)
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PagamentoService:

    @staticmethod
    def criar_preferencia_pagamento(pedido_id):
        # Cria preferência de pagamento no Mercado Pago (Checkout Pro)
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
        Atualiza status e cria envio automaticamente quando aprovado.
        """
        mp_service = MercadoPagoService()
        webhook_info = mp_service.processar_webhook(data)

        if not webhook_info:
            return None

        payment_id = webhook_info.get("payment_id")

        if not payment_id:
            logger.debug("Webhook sem payment_id, ignorando")
            return None

        # Buscar transação pelo payment_id
        transacao = TransacaoPagamento.query.filter_by(
            mp_payment_id=str(payment_id)
        ).first()

        if not transacao:
            # Buscar pelo pedido_id
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

        # Mapear status
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

        # Obter pedido
        pedido = transacao.pedido

        # Evitar processar webhook duplicado
        if (
            pedido.status == StatusPedidoEnum.EM_SEPARACAO
            and novo_status == StatusPagamentoEnum.APROVADO
        ):
            logger.info(
                f"Pedido #{pedido.id} já processado, ignorando webhook duplicado"
            )
            return {
                "transacao_id": transacao.id,
                "pedido_id": pedido.id,
                "status_anterior": status_anterior.value,
                "status_novo": novo_status.value,
                "pedido_status": pedido.status.value,
                "duplicado": True,
            }

        # Processar de acordo com o status
        if novo_status == StatusPagamentoEnum.APROVADO:
            pedido.status = StatusPedidoEnum.PAGO
            logger.info(
                f"Pedido #{pedido.id} aprovado - R$ {float(pedido.valor_total):.2f}"
            )

            # Criar envio no Melhor Envio
            try:
                logger.info(f"Processando envio do pedido #{pedido.id}")

                # 1. Criar pedido no Melhor Envio
                resultado_me = criar_pedido_melhor_envio(pedido)
                pedido.melhor_envio_id = resultado_me.get("melhor_envio_id")
                pedido.melhor_envio_protocolo = resultado_me.get("protocol")

                # 2. Verificar e atualizar serviço se mudou
                servico_usado = resultado_me.get("service_name", pedido.frete_tipo)
                if servico_usado and servico_usado != pedido.frete_tipo:
                    logger.warning(
                        f"Serviço alterado: {pedido.frete_tipo} → {servico_usado}"
                    )
                    pedido.frete_servico_nome = servico_usado

                # 3. Verificar e atualizar preço se mudou
                preco_real = resultado_me.get("price")
                if preco_real:
                    # ✅ CONVERTER TUDO PARA DECIMAL
                    preco_cotado = Decimal(str(pedido.frete_valor))
                    preco_real_decimal = Decimal(str(preco_real))
                    diferenca = preco_real_decimal - preco_cotado

                    # Se diferença maior que R$ 0.10, atualizar
                    if abs(diferenca) > Decimal("0.10"):
                        logger.warning(
                            f"Preço frete atualizado: "
                            f"R$ {float(preco_cotado):.2f} → R$ {float(preco_real_decimal):.2f} "
                            f"(diferença: R$ {float(abs(diferenca)):.2f})"
                        )

                        # Atualizar valores (tudo em Decimal)
                        pedido.frete_valor = preco_real_decimal
                        pedido.valor_total = pedido.valor_total + diferenca

                # 4. Comprar o frete
                comprar_envio(pedido.melhor_envio_id)

                # 5. Gerar etiqueta
                gerar_etiqueta(pedido.melhor_envio_id)

                # 6. Obter link da etiqueta
                etiqueta_url = imprimir_etiqueta(pedido.melhor_envio_id)
                pedido.etiqueta_url = etiqueta_url

                # 7. Atualizar status para EM_SEPARACAO
                pedido.status = StatusPedidoEnum.EM_SEPARACAO

                logger.info(
                    f"Envio processado: {pedido.melhor_envio_protocolo} | "
                    f"Etiqueta: {etiqueta_url}"
                )

            except Exception as e:
                logger.error(
                    f"Erro ao processar envio do pedido #{pedido.id}: {str(e)}"
                )
                # Não falha o pagamento por causa do envio
                # Pedido fica PAGO e pode ser enviado manualmente depois

        elif novo_status == StatusPagamentoEnum.REJEITADO:
            pedido.status = StatusPedidoEnum.CANCELADO
            logger.warning(f"Pedido #{pedido.id} rejeitado")

        elif novo_status == StatusPagamentoEnum.REEMBOLSADO:
            pedido.status = StatusPedidoEnum.CANCELADO
            PagamentoService._reverter_estoque(pedido)
            logger.info(f"Pedido #{pedido.id} estornado e estoque revertido")

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
                logger.debug(f"Estoque revertido: {produto.nome} +{item.quantidade}")

    @staticmethod
    def estornar_pagamento(transacao_id, valor=None):
        # Estorna um pagamento (total ou parcial)
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

        logger.info(
            f"Estorno processado: Pedido #{transacao.pedido.id} - "
            f"R$ {resultado['amount']}"
        )

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

        # Se tiver payment_id, consultar status atualizado no MP
        if transacao.mp_payment_id:
            try:
                mp_service = MercadoPagoService()
                pagamento_mp = mp_service.consultar_pagamento(transacao.mp_payment_id)

                # Mapear status
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
                logger.error(f"Erro ao consultar MP: {e}")

        return transacao
