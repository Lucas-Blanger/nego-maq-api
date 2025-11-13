from flask import Blueprint, request, jsonify
from services.public.AuthService import (
    registrar as registrar_service,
    login as login_service,
    solicitar_recuperacao_senha as solicitar_recuperacao_service,
    verificar_codigo_e_redefinir_senha as verificar_codigo_service,
    editar_perfil as editar_perfil_service,
)
from utils.formatters.user_formatter import formatar_dados_usuario
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
                    "usuario": formatar_dados_usuario(usuario),
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
                    "usuario": formatar_dados_usuario(usuario),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"erro": str(e)}), 401


# SOLICITAR CÓDIGO DE RECUPERAÇÃO
@auth_routes.route("/recuperar/solicitar", methods=["POST"])
def solicitar_recuperacao():
    try:
        data = request.get_json()
        email = data.get("email")

        if not email:
            return jsonify({"erro": "Email é obrigatório"}), 400

        solicitar_recuperacao_service(email)
        return (
            jsonify({"mensagem": "Código de recuperação enviado para seu email"}),
            200,
        )

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


# VERIFICAR CÓDIGO E REDEFINIR SENHA
@auth_routes.route("/recuperar/verificar", methods=["POST"])
def verificar_codigo_recuperacao():
    try:
        data = request.get_json()
        email = data.get("email")
        codigo = data.get("codigo")
        nova_senha = data.get("nova_senha")

        if not email or not codigo or not nova_senha:
            return jsonify({"erro": "Email, código e nova senha são obrigatórios"}), 400

        verificar_codigo_service(email, codigo, nova_senha)
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
        )
        return (
            jsonify(
                {
                    "mensagem": "Perfil atualizado com sucesso",
                    "usuario": formatar_dados_usuario(usuario),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
