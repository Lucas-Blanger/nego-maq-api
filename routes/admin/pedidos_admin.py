from flask import Blueprint, request, jsonify
from services.admin.admin_pedidos_service import (
    listar_pedidos as listar_pedidos_service,
    atualizar_pedido as atualizar_pedido_service,
    deletar_pedido as deletar_pedido_service,
    atualizar_item as atualizar_item_service,
    deletar_item as deletar_item_service,
    atualizar_transacao as atualizar_transacao_service,
)
from instance.config import ADMIN_TOKEN

admin_pedidos_routes = Blueprint("admin_pedidos", __name__, url_prefix="/admin_pedidos")


# Função para verificar se o token do admin é válido
def verificar_token():
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    if token != ADMIN_TOKEN:
        raise PermissionError("Não autorizado")
    return True


# PEDIDOS


# Listar todos os pedidos cadastrados
@admin_pedidos_routes.route("/pedidos", methods=["GET"])
def listar_pedidos():
    try:
        verificar_token()
        resultado = listar_pedidos_service()
        return jsonify(resultado), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403


# Atualizar informações de um pedido específico
@admin_pedidos_routes.route("/pedidos/<pedido_id>", methods=["PUT"])
def atualizar_pedido(pedido_id):
    try:
        verificar_token()
        data = request.get_json() or {}
        atualizar_pedido_service(pedido_id, data)
        return jsonify({"mensagem": "Pedido atualizado com sucesso"}), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


# Deletar um pedido específico
@admin_pedidos_routes.route("/pedidos/<pedido_id>", methods=["DELETE"])
def deletar_pedido(pedido_id):
    try:
        verificar_token()
        deletar_pedido_service(pedido_id)
        return jsonify({"mensagem": "Pedido excluído"}), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404


# ITENS


# Atualizar um item dentro de um pedido
@admin_pedidos_routes.route("/itens/<item_id>", methods=["PUT"])
def atualizar_item(item_id):
    try:
        verificar_token()
        data = request.get_json() or {}
        atualizar_item_service(item_id, data)
        return jsonify({"mensagem": "Item atualizado"}), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404


# Deletar um item de um pedido
@admin_pedidos_routes.route("/itens/<item_id>", methods=["DELETE"])
def deletar_item(item_id):
    try:
        verificar_token()
        deletar_item_service(item_id)
        return jsonify({"mensagem": "Item removido"}), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404


# TRANSAÇÕES


# Atualizar dados de uma transação relacionada a um pedido
@admin_pedidos_routes.route("/transacoes/<transacao_id>", methods=["PUT"])
def atualizar_transacao(transacao_id):
    try:
        verificar_token()
        data = request.get_json() or {}
        atualizar_transacao_service(transacao_id, data)
        return jsonify({"mensagem": "Transação atualizada"}), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
