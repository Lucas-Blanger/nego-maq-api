from flask import Blueprint, request, jsonify
from services.public.auth_service import (
    registrar as registrar_service,
    login as login_service,
    recuperar_senha as recuperar_senha_service,
    editar_perfil as editar_perfil_service,
)
from utils.crypto_utils import descriptografar_cpf
from utils.middlewares.auth import token_required

auth_routes = Blueprint("auth", __name__, url_prefix="/auth")


# REGISTRO
@auth_routes.route("/registrar", methods=["POST"])
def registrar():
    try:
        data = request.get_json()
        usuario, token = registrar_service(
            nome=data["nome"],
            sobrenome=data["sobrenome"],
            email=data["email"],
            telefone=data["telefone"],
            cpf=data.get("cpf"),
            senha=data["senha"],
            is_admin=data.get("is_admin", False),
        )
        return (
            jsonify(
                {
                    "mensagem": "Usuário criado com sucesso",
                    "token": token,
                    "usuario": {
                        "id": usuario.id,
                        "nome": usuario.nome,
                        "sobrenome": usuario.sobrenome,
                        "email": usuario.email,
                        "telefone": usuario.telefone,
                        "cpf": descriptografar_cpf(usuario.cpf),
                        "is_admin": usuario.is_admin,
                    },
                }
            ),
            201,
        )
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


# LOGIN
@auth_routes.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        usuario, token = login_service(data["email"], data["senha"])
        return (
            jsonify(
                {
                    "mensagem": "Login realizado com sucesso",
                    "token": token,
                    "usuario": {
                        "id": usuario.id,
                        "nome": usuario.nome,
                        "sobrenome": usuario.sobrenome,
                        "email": usuario.email,
                        "telefone": usuario.telefone,
                        "cpf": descriptografar_cpf(usuario.cpf),
                        "is_admin": usuario.is_admin,
                    },
                }
            ),
            200,
        )
    except ValueError as e:
        return jsonify({"erro": str(e)}), 401


#  RECUPERAÇÃO DE SENHA
@auth_routes.route("/recuperar", methods=["POST"])
def recuperar_senha():
    try:
        data = request.get_json()
        usuario = recuperar_senha_service(data.get("email"), data.get("nova_senha"))
        return jsonify({"mensagem": "Senha atualizada com sucesso"}), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@auth_routes.route("/editar", methods=["PUT"])
@token_required
def editar_perfil(payload):
    try:
        data = request.get_json()
        usuario = editar_perfil_service(
            email_atual=payload["email"],
            novo_nome=data.get("novo_nome"),
            novo_sobrenome=data.get("novo_sobrenome"),
            novo_email=data.get("novo_email"),
            novo_telefone=data.get("novo_telefone"),
            novo_cpf=data.get("novo_cpf"),
            nova_senha=data.get("nova_senha"),
        )
        return (
            jsonify(
                {
                    "mensagem": "Perfil atualizado com sucesso",
                    "usuario": {
                        "id": usuario.id,
                        "nome": usuario.nome,
                        "sobrenome": usuario.sobrenome,
                        "email": usuario.email,
                        "telefone": usuario.telefone,
                        "cpf": descriptografar_cpf(usuario.cpf),
                        "is_admin": usuario.is_admin,
                    },
                }
            ),
            200,
        )
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
