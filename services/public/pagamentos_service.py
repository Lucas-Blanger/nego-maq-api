from database import db
from database.models import (
    Pedido,
    TransacaoPagamento,
    StatusPagamentoEnum,
    StatusPedidoEnum,
)


class PagamentoService:

    # Cria uma transação para um pedido
    @staticmethod
    def criar_transacao(pedido_id, valor, metodo_pagamento):
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            raise ValueError("Pedido não encontrado")

        # Verifica se valor e método de pagamento foram fornecidos
        if valor is None or metodo_pagamento is None:
            raise ValueError("Valor e método de pagamento são obrigatórios")

        # Verifica se valor da transação bate com valor total do pedido
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

        # Atualiza status do pedido com base no status da transação
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

    # Lista todas as transações de um pedido
    @staticmethod
    def listar_transacoes(pedido_id):
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            raise ValueError("Pedido não encontrado")
        return pedido.transacoes
