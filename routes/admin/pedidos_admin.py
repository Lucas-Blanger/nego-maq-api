from flask import Blueprint, request, jsonify
from services.admin.AdminPedidosService import (
    listar_pedidos as listar_pedidos_service,
    atualizar_pedido as atualizar_pedido_service,
    deletar_pedido as deletar_pedido_service,
    atualizar_item as atualizar_item_service,
    deletar_item as deletar_item_service,
    atualizar_transacao as atualizar_transacao_service,
)
from datetime import timedelta
from utils.middlewares.auth import admin_required

admin_pedidos_routes = Blueprint("admin_pedidos", __name__, url_prefix="/admin_pedidos")

# PEDIDOS


# Listar todos os pedidos cadastrados
@admin_pedidos_routes.route("/pedidos", methods=["GET"])
@admin_required
def listar_pedidos():
    try:
        data_inicial = request.args.get("dataInicial")  # Ex: 2025-01-01
        data_final = request.args.get("dataFinal")  # Ex: 2025-12-31
        categoria_id = request.args.get("categoriaId")  # Ex: 1, 2, 3 ou 4

        from datetime import datetime, timedelta

        if data_inicial:
            data_inicial = datetime.fromisoformat(data_inicial)

        if data_final:
            data_final = datetime.fromisoformat(data_final) + timedelta(days=1)

        if categoria_id:
            categoria_id = int(categoria_id)

        pedidos = listar_pedidos_service(
            data_inicial=data_inicial, data_final=data_final, categoria_id=categoria_id
        )

        return jsonify(pedidos), 200

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": "Erro ao listar pedidos", "detalhes": str(e)}), 500


# Atualizar informações de um pedido específico
@admin_pedidos_routes.route("/pedidos/<pedido_id>", methods=["PUT"])
@admin_required
def atualizar_pedido(pedido_id):
    try:
        data = request.get_json() or {}
        atualizar_pedido_service(pedido_id, data)
        return jsonify({"mensagem": "Pedido atualizado com sucesso"}), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


# Deletar um pedido específico
@admin_pedidos_routes.route("/pedidos/<pedido_id>", methods=["DELETE"])
@admin_required
def deletar_pedido(pedido_id):
    try:
        deletar_pedido_service(pedido_id)
        return jsonify({"mensagem": "Pedido excluído"}), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404


# ITENS


# Atualizar um item dentro de um pedido
@admin_pedidos_routes.route("/itens/<item_id>", methods=["PUT"])
@admin_required
def atualizar_item(item_id):
    try:
        data = request.get_json() or {}
        atualizar_item_service(item_id, data)
        return jsonify({"mensagem": "Item atualizado"}), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404


# Deletar um item de um pedido
@admin_pedidos_routes.route("/itens/<item_id>", methods=["DELETE"])
@admin_required
def deletar_item(item_id):
    try:
        deletar_item_service(item_id)
        return jsonify({"mensagem": "Item removido"}), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404


# TRANSAÇÕES


# Atualizar dados de uma transação relacionada a um pedido
@admin_pedidos_routes.route("/transacoes/<transacao_id>", methods=["PUT"])
@admin_required
def atualizar_transacao(transacao_id):
    try:
        data = request.get_json() or {}
        atualizar_transacao_service(transacao_id, data)
        return jsonify({"mensagem": "Transação atualizada"}), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
