from flask import Blueprint, request, jsonify
from services.public.melhor_envio_service import calcular_frete
from utils.middlewares.auth import token_required

frete_routes = Blueprint("frete", __name__, url_prefix="/frete")


@frete_routes.route("/calcular-frete", methods=["POST"])
@token_required
def calcular(payload):
    data = request.json
    try:
        resultado = calcular_frete(
            from_postal_code=data["from"],
            to_postal_code=data["sto"],
            weight=data["weight"],
            height=data["height"],
            width=data["width"],
            length=data["length"],
        )

        # Retorna as opções de frete formatadas
        opcoes = []
        for opcao in resultado:
            opcoes.append(
                {
                    "transportadora": opcao.get("company", {}).get("name"),
                    "servico": opcao.get("name"),
                    "preco": opcao.get("price"),
                    "prazo_dias": opcao.get("delivery_time"),
                    "delivery_range": opcao.get("delivery_range", {}),
                }
            )

        return jsonify({"opcoes": opcoes}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
