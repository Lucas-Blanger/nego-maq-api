from flask import Flask, request, jsonify, Blueprint
from database.models import (
    db,
    Pedido,
    ItemPedido,
    TransacaoPagamento,
    Produto,
    StatusPedidoEnum,
    StatusPagamentoEnum,
)
import uuid

app = Flask(__name__)
public_routes_pedidos = Blueprint("pedidos_public", __name__)


# PEDIDOS PÚBLICOS


# Criar um novo pedido
@public_routes_pedidos.route("/pedidos", methods=["POST"])
def criar_pedido():
    data = request.json
    usuario_id = data.get("usuario_id")
    itens = data.get("itens", [])  # lista de {produto_id, quantidade}

    if not itens:
        return jsonify({"error": "O pedido precisa ter ao menos um item"}), 400

    pedido = Pedido(usuario_id=usuario_id, valor_total=0)
    db.session.add(pedido)
    db.session.flush()  # gera o ID do pedido

    total = 0
    for item_data in itens:
        produto = Produto.query.get(item_data["produto_id"])
        if not produto:
            db.session.rollback()
            return (
                jsonify({"error": f"Produto {item_data['produto_id']} não encontrado"}),
                404,
            )

        quantidade = item_data.get("quantidade", 1)
        preco_unitario = produto.preco
        total += preco_unitario * quantidade

        item = ItemPedido(
            pedido_id=pedido.id,
            produto_id=produto.id,
            quantidade=quantidade,
            preco_unitario=preco_unitario,
        )
        db.session.add(item)

    pedido.valor_total = total
    db.session.commit()
    return (
        jsonify({"pedido_id": pedido.id, "valor_total": float(pedido.valor_total)}),
        201,
    )


# Obter detalhes de um pedido
@public_routes_pedidos.route("/pedidos/<pedido_id>", methods=["GET"])
def obter_pedido(pedido_id):
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({"error": "Pedido não encontrado"}), 404

    itens = [
        {
            "produto_id": item.produto_id,
            "quantidade": item.quantidade,
            "preco_unitario": float(item.preco_unitario),
        }
        for item in pedido.itens
    ]

    transacoes = [
        {
            "id": t.id,
            "valor": float(t.valor),
            "status": t.status.name,
            "metodo_pagamento": t.metodo_pagamento,
        }
        for t in pedido.transacoes
    ]

    return jsonify(
        {
            "pedido_id": pedido.id,
            "usuario_id": pedido.usuario_id,
            "valor_total": float(pedido.valor_total),
            "status": pedido.status.name,
            "itens": itens,
            "transacoes": transacoes,
        }
    )


# Listar pedidos de um usuário
@public_routes_pedidos.route("/usuarios/<usuario_id>/pedidos", methods=["GET"])
def pedidos_usuario(usuario_id):
    pedidos = Pedido.query.filter_by(usuario_id=usuario_id).all()
    resultado = []
    for p in pedidos:
        resultado.append(
            {
                "pedido_id": p.id,
                "valor_total": float(p.valor_total),
                "status": p.status.name,
            }
        )
    return jsonify(resultado), 200


# TRANSACOES PÚBLICAS


# Criar uma transação de pagamento
@public_routes_pedidos.route("/pedidos/<pedido_id>/transacoes", methods=["POST"])
def criar_transacao(pedido_id):
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({"error": "Pedido não encontrado"}), 404

    data = request.json or {}
    valor = data.get("valor")
    metodo = data.get("metodo_pagamento")

    # validações
    if valor is None or metodo is None:
        return jsonify({"error": "Valor e método de pagamento são obrigatórios"}), 400

    # garantir que valor enviado bate com o valor do pedido
    if float(valor) != float(pedido.valor_total):
        return (
            jsonify(
                {
                    "error": "O valor da transação deve ser igual ao valor total do pedido"
                }
            ),
            400,
        )

    # criar a transação
    transacao = TransacaoPagamento(
        pedido_id=pedido.id,
        valor=valor,
        metodo_pagamento=metodo,
    )
    db.session.add(transacao)

    # se o pagamento for aprovado já no momento da criação
    if transacao.status == StatusPagamentoEnum.APROVADO:
        pedido.status = StatusPedidoEnum.PAGO
    elif transacao.status in [
        StatusPagamentoEnum.RECUSADO,
        StatusPagamentoEnum.ESTORNADO,
    ]:
        pedido.status = StatusPedidoEnum.CANCELADO

    db.session.commit()

    return (
        jsonify(
            {
                "transacao_id": transacao.id,
                "pedido_id": pedido.id,
                "valor": float(transacao.valor),
                "status": transacao.status.value,  # .value = "Pendente", etc
                "metodo_pagamento": transacao.metodo_pagamento,
                "pedido_status": pedido.status.value,
            }
        ),
        201,
    )


# Listar transações de um pedido
@public_routes_pedidos.route("/pedidos/<pedido_id>/transacoes", methods=["GET"])
def listar_transacoes(pedido_id):
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({"error": "Pedido não encontrado"}), 404

    resultado = [
        {
            "id": t.id,
            "valor": float(t.valor),
            "status": t.status.name,
            "metodo_pagamento": t.metodo_pagamento,
        }
        for t in pedido.transacoes
    ]
    return jsonify(resultado), 200
