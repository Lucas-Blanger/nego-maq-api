from flask import Blueprint, request, jsonify
from services.admin.admin_enderecos_service import (
    listar_enderecos as listar_enderecos_service,
    atualizar_endereco as atualizar_endereco_service,
    deletar_endereco as deletar_endereco_service,
)
from instance.config import ADMIN_TOKEN

admin_enderecos_routes = Blueprint(
    "admin_enderecos", __name__, url_prefix="/admin_enderecos"
)


# Função de autenticação via token (somente admin pode acessar essas rotas)
def verificar_token():
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    if token != ADMIN_TOKEN:
        raise PermissionError("Não autorizado")
    return True


# ROTAS DE ENDEREÇOS


# Listar todos os endereços cadastrados
@admin_enderecos_routes.route("/enderecos", methods=["GET"])
def listar_enderecos_route():
    try:
        verificar_token()
        resultado = listar_enderecos_service()
        return jsonify(resultado), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403


# Atualizar dados de um endereço específico
@admin_enderecos_routes.route("/enderecos/<endereco_id>", methods=["PUT"])
def atualizar_endereco_route(endereco_id):
    try:
        verificar_token()
        data = request.get_json() or {}
        atualizar_endereco_service(endereco_id, data)
        return jsonify({"mensagem": "Endereço atualizado com sucesso"}), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404


# Deletar um endereço pelo ID
@admin_enderecos_routes.route("/enderecos/<endereco_id>", methods=["DELETE"])
def deletar_endereco_route(endereco_id):
    try:
        verificar_token()
        deletar_endereco_service(endereco_id)
        return jsonify({"mensagem": "Endereço excluído"}), 200
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404
