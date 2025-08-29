from flask import Blueprint, request, jsonify
from database.models import db, Pedido, ItemPedido, TransacaoPagamento, Produto, Usuario
from database.models import StatusPedidoEnum, StatusPagamentoEnum
from config import ADMIN_TOKEN

admin_pedidos_routes = Blueprint("admin_pedidos", __name__, url_prefix="/admin_pedidos")

# PEDIDOS ADMIN


# Listar todos os pedidos
@admin_pedidos_routes.route("/pedidos", methods=["GET"])
def listar_pedidos():
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    if token != ADMIN_TOKEN:
        return jsonify({"erro": "Não autorizado"}), 403

    pedidos = Pedido.query.all()
    resultado = []
    for p in pedidos:
        resultado.append(
            {
                "id": p.id,
                "usuario_id": p.usuario_id,
                "valor_total": float(p.valor_total),
                "status": p.status.name,
                "criado_em": p.criado_em,
            }
        )
    return jsonify(resultado), 200


# Atualizar status do pedido
@admin_pedidos_routes.route("/pedidos/<pedido_id>", methods=["PUT"])
def atualizar_pedido(pedido_id):
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    if token != ADMIN_TOKEN:
        return jsonify({"erro": "Não autorizado"}), 403

    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    data = request.get_json()
    status = data.get("status")
    frete_valor = data.get("frete_valor")
    frete_tipo = data.get("frete_tipo")

    if status:
        try:
            pedido.status = StatusPedidoEnum[status.upper()]
        except KeyError:
            return jsonify({"erro": "Status inválido"}), 400

    if frete_valor is not None:
        pedido.frete_valor = frete_valor
    if frete_tipo:
        pedido.frete_tipo = frete_tipo

    db.session.commit()
    return jsonify({"mensagem": "Pedido atualizado com sucesso"}), 200


# Cancelar/excluir pedido
@admin_pedidos_routes.route("/pedidos/<pedido_id>", methods=["DELETE"])
def deletar_pedido(pedido_id):
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    if token != ADMIN_TOKEN:
        return jsonify({"erro": "Não autorizado"}), 403

    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    db.session.delete(pedido)
    db.session.commit()
    return jsonify({"mensagem": "Pedido excluído"}), 200


# ITENS ADMIN


# Atualizar item do pedido
@admin_pedidos_routes.route("/itens/<item_id>", methods=["PUT"])
def atualizar_item(item_id):
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    if token != ADMIN_TOKEN:
        return jsonify({"erro": "Não autorizado"}), 403

    item = ItemPedido.query.get(item_id)
    if not item:
        return jsonify({"erro": "Item não encontrado"}), 404

    data = request.get_json()
    if "quantidade" in data:
        item.quantidade = data["quantidade"]
    if "preco_unitario" in data:
        item.preco_unitario = data["preco_unitario"]

    db.session.commit()
    return jsonify({"mensagem": "Item atualizado"})


# Remover item do pedido
@admin_pedidos_routes.route("/itens/<item_id>", methods=["DELETE"])
def deletar_item(item_id):
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    if token != ADMIN_TOKEN:
        return jsonify({"erro": "Não autorizado"}), 403

    item = ItemPedido.query.get(item_id)
    if not item:
        return jsonify({"erro": "Item não encontrado"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"mensagem": "Item removido"})


# TRANSAÇÕES ADMIN


# Atualizar status da transação
@admin_pedidos_routes.route("/transacoes/<transacao_id>", methods=["PUT"])
def atualizar_transacao(transacao_id):
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    if token != ADMIN_TOKEN:
        return jsonify({"erro": "Não autorizado"}), 403

    transacao = TransacaoPagamento.query.get(transacao_id)
    if not transacao:
        return jsonify({"erro": "Transação não encontrada"}), 404

    data = request.get_json()
    status = data.get("status")
    if status:
        try:
            transacao.status = StatusPagamentoEnum[status.upper()]
        except KeyError:
            return jsonify({"erro": "Status inválido"}), 400

    db.session.commit()
    return jsonify({"mensagem": "Transação atualizada"})
