from functools import wraps
from flask import request, jsonify, current_app
from instance.config import ADMIN_TOKEN
import jwt


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token.split(" ")[1]
        if token != ADMIN_TOKEN:
            return jsonify({"erro": "Não autorizado"}), 403
        return f(*args, **kwargs)

    return wrapper


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return jsonify({"erro": "Token ausente"}), 401

        token = token.split(" ")[1]

        if token == ADMIN_TOKEN:
            payload = {"is_admin": True}
        else:
            try:
                payload = jwt.decode(
                    token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
                )
            except jwt.ExpiredSignatureError:
                return jsonify({"erro": "Token expirado"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"erro": "Token inválido"}), 401

        return f(payload, *args, **kwargs)

    return wrapper