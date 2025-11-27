from database import db
from database.models import Pedido, ItemPedido, TransacaoPagamento, Produto, pedido
from database.models import StatusPedidoEnum, StatusPagamentoEnum

CATEGORIAS_MAP = {1: "facas", 2: "aventais", 3: "estojos", 4: "churrascos"}


# Listar todos os pedidos
def listar_pedidos(data_inicial=None, data_final=None, categoria_id=None):
    categoria = None
    if categoria_id is not None:
        categoria = CATEGORIAS_MAP.get(categoria_id)
        if not categoria:
            raise ValueError(
                f"Categoria ID inválida. IDs aceitos: {list(CATEGORIAS_MAP.keys())}"
            )

    query = Pedido.query

    filtros = []

    if data_inicial:
        filtros.append(Pedido.criado_em >= data_inicial)

    if data_final:
        filtros.append(Pedido.criado_em <= data_final)

    if categoria:
        query = (
            query.join(ItemPedido).join(Produto).filter(Produto.categoria == categoria)
        )

    if filtros:
        query = query.filter(*filtros)

    if categoria:
        query = query.distinct()

    pedidos = query.all()

    resultado = []
    for p in pedidos:
        resultado.append(
            {
                "id": p.id,
                "usuario_id": p.usuario_id,
                "valor_total": float(p.valor_total),
                "nome": p.usuario.nome if p.usuario else None,
                "status": p.status.name,
                "criado_em": p.criado_em.isoformat() if p.criado_em else None,
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

    # Apagar todos os itens relacionados
    ItemPedido.query.filter_by(pedido_id=pedido_id).delete()

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
