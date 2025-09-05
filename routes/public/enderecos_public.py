from flask import Blueprint, request, jsonify
from services.public.endereco_service import (
    criar_endereco as criar_endereco_service,
    listar_enderecos_usuario as listar_enderecos_usuario_service,
    obter_endereco as obter_endereco_service,
)
from utils.auth import token_required

public_enderecos_routes = Blueprint("enderecos_public", __name__)

# CRIAR ENDEREÇO


# Criar um novo endereço para o usuário
@public_enderecos_routes.route("/usuarios/<usuario_id>/enderecos", methods=["POST"])
@token_required
def criar_endereco(payload, usuario_id):
    try:
        if payload["id"] != usuario_id and not payload["is_admin"]:
            return jsonify({"erro": "Acesso não autorizado"}), 403

        data = request.get_json() or {}
        endereco = criar_endereco_service(usuario_id, data)
        return (
            jsonify(
                {"mensagem": "Endereço criado com sucesso", "endereco_id": endereco.id}
            ),
            201,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# Listar endereços de um usuário
@public_enderecos_routes.route("/usuarios/<usuario_id>/enderecos", methods=["GET"])
@token_required
def listar_enderecos_usuario(payload, usuario_id):
    if payload["id"] != usuario_id and not payload["is_admin"]:
        return jsonify({"erro": "Acesso não autorizado"}), 403

    enderecos = listar_enderecos_usuario_service(usuario_id)
    resultado = [
        {
            "id": e.id,
            "cep": e.cep,
            "logradouro": e.logradouro,
            "numero": e.numero,
            "complemento": e.complemento,
            "bairro": e.bairro,
            "cidade": e.cidade,
            "estado": e.estado,
        }
        for e in enderecos
    ]
    return jsonify(resultado), 200


# Obter detalhes de um endereço específico
@public_enderecos_routes.route("/enderecos/<endereco_id>", methods=["GET"])
@token_required
def obter_endereco(payload, endereco_id):
    endereco = obter_endereco_service(endereco_id)
    if not endereco:
        return jsonify({"error": "Endereço não encontrado"}), 404

    if payload["id"] != endereco.usuario_id and not payload["is_admin"]:
        return jsonify({"erro": "Acesso não autorizado"}), 403

    return (
        jsonify(
            {
                "id": endereco.id,
                "usuario_id": endereco.usuario_id,
                "cep": endereco.cep,
                "logradouro": endereco.logradouro,
                "numero": endereco.numero,
                "complemento": endereco.complemento,
                "bairro": endereco.bairro,
                "cidade": endereco.cidade,
                "estado": endereco.estado,
            }
        ),
        200,
    )
