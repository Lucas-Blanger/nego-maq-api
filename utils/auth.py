from flask import request, jsonify
from instance.config import ADMIN_TOKEN
from functools import wraps


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
