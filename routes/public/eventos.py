from flask import Blueprint, request, jsonify
from services.public.evento_service import (
    registrar_evento as registrar_evento_service,
    top_vendas as top_vendas_service,
    recomendacoes as recomendacoes_service,
)

evento_routes = Blueprint("eventos", __name__, url_prefix="/eventos")

# REGISTRAR EVENTO


@evento_routes.route("/registrar_evento", methods=["POST"])
def registrar_evento():
    dados = request.json
    registrar_evento_service(
        usuario_id=dados.get("usuario_id"),
        produto_id=dados.get("produto_id"),
        tipo_evento=dados.get("tipo_evento"),
    )
    return jsonify({"mensagem": "Evento registrado com sucesso!"}), 201


# ANÁLISE: TOP VENDAS
@evento_routes.route("/analise/top_vendas", methods=["GET"])
def top_vendas():
    resultados = top_vendas_service()
    return jsonify(resultados)


# RECOMENDAÇÕES DE PRODUTOS
@evento_routes.route("/recomendacoes/<int:produto_id>", methods=["GET"])
def recomendacoes(produto_id):
    resultados = recomendacoes_service(produto_id)
    return jsonify(resultados)
