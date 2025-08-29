from flask import Blueprint, request, jsonify
from database.models import db, Endereco, Usuario
from config import ADMIN_TOKEN

admin_enderecos_routes = Blueprint(
    "admin_enderecos", __name__, url_prefix="/admin_enderecos"
)


# Middleware de autenticação admin
def validar_token():
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    return token == ADMIN_TOKEN


# Listar todos os endereços
@admin_enderecos_routes.route("/enderecos", methods=["GET"])
def listar_enderecos():
    if not validar_token():
        return jsonify({"erro": "Não autorizado"}), 403

    enderecos = Endereco.query.all()
    resultado = []
    for e in enderecos:
        resultado.append(
            {
                "id": e.id,
                "usuario_id": e.usuario_id,
                "cep": e.cep,
                "logradouro": e.logradouro,
                "numero": e.numero,
                "complemento": e.complemento,
                "bairro": e.bairro,
                "cidade": e.cidade,
                "estado": e.estado,
            }
        )
    return jsonify(resultado), 200


# Atualizar um endereço
@admin_enderecos_routes.route("/enderecos/<endereco_id>", methods=["PUT"])
def atualizar_endereco(endereco_id):
    if not validar_token():
        return jsonify({"erro": "Não autorizado"}), 403

    endereco = Endereco.query.get(endereco_id)
    if not endereco:
        return jsonify({"erro": "Endereço não encontrado"}), 404

    data = request.get_json() or {}
    for campo in [
        "cep",
        "logradouro",
        "numero",
        "complemento",
        "bairro",
        "cidade",
        "estado",
    ]:
        if campo in data:
            setattr(endereco, campo, data[campo])

    db.session.commit()
    return jsonify({"mensagem": "Endereço atualizado com sucesso"}), 200


# Deletar um endereço
@admin_enderecos_routes.route("/enderecos/<endereco_id>", methods=["DELETE"])
def deletar_endereco(endereco_id):
    if not validar_token():
        return jsonify({"erro": "Não autorizado"}), 403

    endereco = Endereco.query.get(endereco_id)
    if not endereco:
        return jsonify({"erro": "Endereço não encontrado"}), 404

    db.session.delete(endereco)
    db.session.commit()
    return jsonify({"mensagem": "Endereço excluído"}), 200
