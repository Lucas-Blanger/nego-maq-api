from flask import Blueprint, request, jsonify
from database.models import db, Endereco, Usuario
import uuid

public_enderecos_routes = Blueprint("enderecos_public", __name__)


# Criar um novo endereço para o usuário
@public_enderecos_routes.route("/usuarios/<usuario_id>/enderecos", methods=["POST"])
def criar_endereco(usuario_id):
    data = request.get_json() or {}

    campos_obrigatorios = ["cep", "logradouro", "numero", "bairro", "cidade", "estado"]
    for campo in campos_obrigatorios:
        if campo not in data:
            return jsonify({"error": f"Campo obrigatório {campo} não informado"}), 400

    endereco = Endereco(
        usuario_id=usuario_id,
        cep=data["cep"],
        logradouro=data["logradouro"],
        numero=data["numero"],
        complemento=data.get("complemento"),
        bairro=data["bairro"],
        cidade=data["cidade"],
        estado=data["estado"],
    )
    db.session.add(endereco)
    db.session.commit()

    return (
        jsonify(
            {"mensagem": "Endereço criado com sucesso", "endereco_id": endereco.id}
        ),
        201,
    )


# Listar endereços de um usuário
@public_enderecos_routes.route("/usuarios/<usuario_id>/enderecos", methods=["GET"])
def listar_enderecos_usuario(usuario_id):
    enderecos = Endereco.query.filter_by(usuario_id=usuario_id).all()
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
def obter_endereco(endereco_id):
    endereco = Endereco.query.get(endereco_id)
    if not endereco:
        return jsonify({"error": "Endereço não encontrado"}), 404

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
