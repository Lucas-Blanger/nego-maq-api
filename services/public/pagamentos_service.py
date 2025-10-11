from database import db
from database.models import (
    Pedido,
    TransacaoPagamento,
    StatusPagamentoEnum,
    StatusPedidoEnum,
)
from services.public.mercadopago_service import MercadoPagoService
from decimal import Decimal


class PagamentoService:
    @staticmethod
    def criar_preferencia_pagamento(pedido_id):
        """
        Cria uma preferência de pagamento no Mercado Pago.
        Retorna o link para checkout.
        """
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
    def processar_pagamento_pix(pedido_id, email_pagador):
        """Processa pagamento via PIX"""
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            raise ValueError("Pedido não encontrado")

        mp_service = MercadoPagoService()
        resultado = mp_service.processar_pagamento_pix(pedido, email_pagador)

        # Criar transação
        transacao = TransacaoPagamento(
            pedido_id=pedido.id,
            valor=pedido.valor_total,
            metodo_pagamento="pix",
            status=StatusPagamentoEnum.PENDENTE,
            mp_payment_id=resultado["payment_id"],
        )
        db.session.add(transacao)
        db.session.commit()

        return {
            "transacao_id": transacao.id,
            "payment_id": resultado["payment_id"],
            "qr_code": resultado["qr_code"],
            "qr_code_base64": resultado["qr_code_base64"],
            "ticket_url": resultado["ticket_url"],
        }

    @staticmethod
    def processar_pagamento_cartao(
        pedido_id, token_cartao, email_pagador, installments=1, issuer_id=None
    ):
        """Processa pagamento via cartão de crédito"""
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            raise ValueError("Pedido não encontrado")

        mp_service = MercadoPagoService()
        resultado = mp_service.processar_pagamento_cartao(
            pedido, token_cartao, email_pagador, installments, issuer_id
        )

        # Mapear status do MP para nosso enum
        status_map = {
            "approved": StatusPagamentoEnum.APROVADO,
            "pending": StatusPagamentoEnum.PENDENTE,
            "in_process": StatusPagamentoEnum.PENDENTE,
            "rejected": StatusPagamentoEnum.RECUSADO,
            "cancelled": StatusPagamentoEnum.CANCELADO,
        }

        status = status_map.get(resultado["status"], StatusPagamentoEnum.PENDENTE)

        # Criar transação
        transacao = TransacaoPagamento(
            pedido_id=pedido.id,
            valor=pedido.valor_total,
            metodo_pagamento="cartao_credito",
            status=status,
            mp_payment_id=resultado["payment_id"],
        )
        db.session.add(transacao)

        # Atualizar status do pedido
        if status == StatusPagamentoEnum.APROVADO:
            pedido.status = StatusPedidoEnum.PAGO
        elif status == StatusPagamentoEnum.RECUSADO:
            pedido.status = StatusPedidoEnum.CANCELADO

        db.session.commit()

        return {
            "transacao_id": transacao.id,
            "payment_id": resultado["payment_id"],
            "status": status.value,
            "status_detail": resultado["status_detail"],
            "pedido_status": pedido.status.value,
        }

    @staticmethod
    def processar_webhook_mercadopago(data):
        """
        Processa notificações do webhook do Mercado Pago.
        Atualiza status da transação e do pedido.
        """
        mp_service = MercadoPagoService()
        webhook_info = mp_service.processar_webhook(data)

        if not webhook_info or webhook_info["type"] != "payment":
            return None

        # Buscar transação pelo payment_id do MP
        transacao = TransacaoPagamento.query.filter_by(
            mp_payment_id=str(webhook_info["payment_id"])
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
            raise ValueError("Transação não encontrada")

        # Mapear status do MP
        status_map = {
            "approved": StatusPagamentoEnum.APROVADO,
            "pending": StatusPagamentoEnum.PENDENTE,
            "in_process": StatusPagamentoEnum.PENDENTE,
            "rejected": StatusPagamentoEnum.RECUSADO,
            "cancelled": StatusPagamentoEnum.CANCELADO,
            "refunded": StatusPagamentoEnum.ESTORNADO,
            "charged_back": StatusPagamentoEnum.ESTORNADO,
        }

        novo_status = status_map.get(
            webhook_info["status"], StatusPagamentoEnum.PENDENTE
        )

        # Atualizar transação
        transacao.status = novo_status

        # Atualizar pedido
        pedido = transacao.pedido
        if novo_status == StatusPagamentoEnum.APROVADO:
            pedido.status = StatusPedidoEnum.PAGO
        elif novo_status == StatusPagamentoEnum.RECUSADO:
            pedido.status = StatusPedidoEnum.CANCELADO
        elif novo_status == StatusPagamentoEnum.ESTORNADO:
            pedido.status = StatusPedidoEnum.CANCELADO
            # Reverter estoque
            PagamentoService._reverter_estoque(pedido)

        db.session.commit()

        return {
            "transacao_id": transacao.id,
            "pedido_id": pedido.id,
            "status_anterior": transacao.status.value,
            "status_novo": novo_status.value,
            "pedido_status": pedido.status.value,
        }

    @staticmethod
    def _reverter_estoque(pedido):
        """Reverte o estoque dos produtos do pedido"""
        from database.models.produto import Produto

        for item in pedido.itens:
            produto = Produto.query.get(item.produto_id)
            if produto:
                produto.estoque += item.quantidade

    @staticmethod
    def estornar_pagamento(transacao_id, valor=None):
        "Estorna um pagamento (total ou parcial)"
        transacao = TransacaoPagamento.query.get(transacao_id)
        if not transacao:
            raise ValueError("Transação não encontrada")

        if not transacao.mp_payment_id:
            raise ValueError("Transação não possui payment_id do Mercado Pago")

        mp_service = MercadoPagoService()
        resultado = mp_service.estornar_pagamento(transacao.mp_payment_id, valor)

        # Atualizar status
        transacao.status = StatusPagamentoEnum.ESTORNADO
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
    def criar_transacao(pedido_id, valor, metodo_pagamento):
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            raise ValueError("Pedido não encontrado")

        if valor is None or metodo_pagamento is None:
            raise ValueError("Valor e método de pagamento são obrigatórios")

        if float(valor) != float(pedido.valor_total):
            raise ValueError(
                "O valor da transação deve ser igual ao valor total do pedido"
            )

        transacao = TransacaoPagamento(
            pedido_id=pedido.id,
            valor=valor,
            metodo_pagamento=metodo_pagamento,
        )
        db.session.add(transacao)

        if transacao.status == StatusPagamentoEnum.APROVADO:
            pedido.status = StatusPedidoEnum.PAGO
        elif transacao.status in [
            StatusPagamentoEnum.RECUSADO,
            StatusPagamentoEnum.ESTORNADO,
        ]:
            pedido.status = StatusPedidoEnum.CANCELADO

        db.session.commit()

        return {
            "transacao_id": transacao.id,
            "pedido_id": pedido.id,
            "valor": float(transacao.valor),
            "status": transacao.status.value,
            "metodo_pagamento": transacao.metodo_pagamento,
            "pedido_status": pedido.status.value,
        }

    @staticmethod
    def listar_transacoes(pedido_id):
        """Lista todas as transações de um pedido"""
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            raise ValueError("Pedido não encontrado")
        return pedido.transacoes
