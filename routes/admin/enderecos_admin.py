from flask import Blueprint, request, jsonify
from services.admin.admin_enderecos_service import (
    listar_enderecos as listar_enderecos_service,
    atualizar_endereco as atualizar_endereco_service,
    deletar_endereco as deletar_endereco_service,
)
from utils.middlewares.auth import admin_required

admin_enderecos_routes = Blueprint(
    "admin_enderecos", __name__, url_prefix="/admin_enderecos"
)

# ROTAS DE ENDEREÇOS


# Listar todos os endereços cadastrados
@admin_enderecos_routes.route("/enderecos", methods=["GET"])
@admin_required
def listar_enderecos_route():
    try:
        resultado = listar_enderecos_service()
        return jsonify(resultado), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403


# Atualizar dados de um endereço específico
@admin_enderecos_routes.route("/enderecos/<endereco_id>", methods=["PUT"])
@admin_required
def atualizar_endereco_route(endereco_id):
    try:
        data = request.get_json() or {}
        atualizar_endereco_service(endereco_id, data)
        return jsonify({"mensagem": "Endereço atualizado com sucesso"}), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404


# Deletar um endereço pelo ID
@admin_enderecos_routes.route("/enderecos/<endereco_id>", methods=["DELETE"])
@admin_required
def deletar_endereco_route(endereco_id):
    try:
        deletar_endereco_service(endereco_id)
        return jsonify({"mensagem": "Endereço excluído"}), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404
