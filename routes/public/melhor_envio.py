from flask import Blueprint, request, jsonify
from services.public.melhor_envio_service import calcular_frete
from utils.middlewares.auth import token_required

frete_routes = Blueprint("frete", __name__, url_prefix="/frete")


@frete_routes.route("/calcular-frete", methods=["POST"])
@token_required
def calcular(payload):
    """
    Calcula frete e retorna opções com TODOS os dados necessários.

    IMPORTANTE: O front-end deve salvar o 'service_id' da opção escolhida!
    """
    data = request.json

    try:
        resultado = calcular_frete(
            from_postal_code=data["from"],
            to_postal_code=data["to"],  # ← CORREÇÃO: era "sto", deveria ser "to"
            weight=data["weight"],
            height=data["height"],
            width=data["width"],
            length=data["length"],
        )
        opcoes = []
        for opcao in resultado:
            opcoes.append(
                {
                    "service_id": opcao.get("id"),
                    # Informações de exibição
                    "transportadora": opcao.get("company", {}).get("name"),
                    "servico": opcao.get("name"),
                    "servico_completo": f"{opcao.get('company', {}).get('name')} - {opcao.get('name')}",
                    # Valores
                    "preco": float(opcao.get("price", 0)),  # Converter para float
                    "preco_formatado": f"R$ {opcao.get('price', 0):.2f}",
                    # Prazos
                    "prazo_dias": opcao.get("delivery_time"),
                    "delivery_range": opcao.get("delivery_range", {}),
                    "prazo_minimo": opcao.get("delivery_range", {}).get("min"),
                    "prazo_maximo": opcao.get("delivery_range", {}).get("max"),
                }
            )

        return jsonify({"opcoes": opcoes, "total_opcoes": len(opcoes)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
