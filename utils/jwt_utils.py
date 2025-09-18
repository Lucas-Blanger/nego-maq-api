import jwt
import datetime
from flask import current_app


def gerar_token(usuario, exp_horas=2):
    # Gera um token JWT para o usuário.
    payload = {
        "id": usuario.id,
        "email": usuario.email,
        "is_admin": usuario.is_admin,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=exp_horas),
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token


def validar_token(token):
    # Decodifica e valida um token JWT.
    try:
        payload = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expirado")
    except jwt.InvalidTokenError:
        raise ValueError("Token inválido")
