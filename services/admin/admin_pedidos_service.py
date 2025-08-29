from database import db
from database.models import Pedido, ItemPedido, TransacaoPagamento
from database.models import StatusPedidoEnum, StatusPagamentoEnum


# Listar todos os pedidos
def listar_pedidos():
    pedidos = Pedido.query.all()
    resultado = []
    for p in pedidos:
        resultado.append(
            {
                "id": p.id,
                "usuario_id": p.usuario_id,
                "valor_total": float(p.valor_total),
                "status": p.status.name,  # Converter enum para string
                "criado_em": p.criado_em,
            }
        )
    return resultado


# Atualizar pedido
def atualizar_pedido(pedido_id, data):
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        raise ValueError("Pedido não encontrado")

    status = data.get("status")
    frete_valor = data.get("frete_valor")
    frete_tipo = data.get("frete_tipo")

    if status:
        try:
            pedido.status = StatusPedidoEnum[status.upper()]  # Atualiza status
        except KeyError:
            raise ValueError("Status inválido")

    if frete_valor is not None:
        pedido.frete_valor = frete_valor  # Atualiza frete valor
    if frete_tipo:
        pedido.frete_tipo = frete_tipo  # Atualiza tipo de frete

    db.session.commit()
    return pedido


# Deletar pedido
def deletar_pedido(pedido_id):
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        raise ValueError("Pedido não encontrado")

    db.session.delete(pedido)
    db.session.commit()
    return pedido


# Atualizar item do pedido
def atualizar_item(item_id, data):
    item = ItemPedido.query.get(item_id)
    if not item:
        raise ValueError("Item não encontrado")

    if "quantidade" in data:
        item.quantidade = data["quantidade"]
    if "preco_unitario" in data:
        item.preco_unitario = data["preco_unitario"]

    db.session.commit()
    return item


# Deletar item do pedido
def deletar_item(item_id):
    item = ItemPedido.query.get(item_id)
    if not item:
        raise ValueError("Item não encontrado")

    db.session.delete(item)
    db.session.commit()
    return item


# Atualizar transação de pagamento
def atualizar_transacao(transacao_id, data):
    transacao = TransacaoPagamento.query.get(transacao_id)
    if not transacao:
        raise ValueError("Transação não encontrada")

    status = data.get("status")
    if status:
        try:
            transacao.status = StatusPagamentoEnum[status.upper()]
        except KeyError:
            raise ValueError("Status inválido")

    db.session.commit()
    return transacao
