from flask import Blueprint, request, jsonify
from instance.config import ADMIN_TOKEN
from services.admin.admin_service import (
    adicionar_produto as adicionar_produto_service,
    deletar_produto as deletar_produto_service,
    atualizar_produto as atualizar_produto_service,
    atualizar_estoque as atualizar_estoque_service,
    criar_promocao as criar_promocao_service,
    remover_promocao as remover_promocao_service,
    get_top_produtos_vendidos,
    get_produtos_mais_visualizados,
    get_total_vendas_periodo,
    get_taxa_conversao,
)
from datetime import datetime

admin_routes = Blueprint("admin", __name__, url_prefix="/admin")


# Função para verificar o token de autenticação do admin
def verificar_token():
    token = request.headers.get("Authorization")
    if not token:
        print("Token ausente")
        raise PermissionError("Token ausente")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    if token != ADMIN_TOKEN:
        raise PermissionError("Não autorizado")
    return True


# ROTAS DE PRODUTOS


# Adicionar um novo produto
@admin_routes.route("/produtos", methods=["POST"])
def adicionar_produto_route():
    try:
        verificar_token()
        data = request.json
        produto = adicionar_produto_service(data)
        return jsonify({"mensagem": "Produto adicionado", "id": produto.id}), 201
    except (ValueError, PermissionError) as e:
        return jsonify({"erro": str(e)}), 400 if isinstance(e, ValueError) else 403


# Deletar um produto existente
@admin_routes.route("/produtos/<produto_id>", methods=["DELETE"])
def deletar_produto_route(produto_id):
    try:
        verificar_token()
        deletar_produto_service(produto_id)
        return jsonify({"mensagem": "Produto removido"}), 200
    except (ValueError, PermissionError) as e:
        return jsonify({"erro": str(e)}), 404 if isinstance(e, ValueError) else 403


# Atualizar os dados de um produto
@admin_routes.route("/produtos/<produto_id>", methods=["PUT"])
def atualizar_produto_route(produto_id):
    try:
        verificar_token()
        data = request.json
        atualizar_produto_service(produto_id, data)
        return (
            jsonify(
                {"mensagem": "Produto atualizado com sucesso", "produto": produto_id}
            ),
            200,
        )
    except (ValueError, PermissionError) as e:
        return jsonify({"erro": str(e)}), 400 if isinstance(e, ValueError) else 403


# Atualizar o estoque de um produto
@admin_routes.route("/estoque/<produto_id>", methods=["PUT"])
def atualizar_estoque_route(produto_id):
    try:
        verificar_token()
        data = request.json
        atualizar_estoque_service(produto_id, data.get("estoque"))
        return (
            jsonify(
                {
                    "mensagem": "Estoque atualizado",
                    "produto_id": produto_id,
                    "estoque": data.get("estoque"),
                }
            ),
            200,
        )
    except (ValueError, PermissionError) as e:
        return jsonify({"erro": str(e)}), 400 if isinstance(e, ValueError) else 403


# ROTAS DE PROMOÇÕES


# Criar promoção para um produto
@admin_routes.route("/produto/promocao/<int:produto_id>", methods=["POST"])
def criar_promocao_route(produto_id):
    try:
        verificar_token()
        data = request.json
        criar_promocao_service(produto_id, data.get("desconto_percentual"))
        return jsonify({"mensagem": "Promoção criada com sucesso"}), 201
    except (ValueError, PermissionError) as e:
        return jsonify({"erro": str(e)}), 400 if isinstance(e, ValueError) else 403


# Remover promoção de um produto
@admin_routes.route("/produto/promocao/<int:produto_id>", methods=["DELETE"])
def remover_promocao_route(produto_id):
    try:
        verificar_token()
        remover_promocao_service(produto_id)
        return jsonify({"mensagem": "Promoção removida com sucesso"}), 200
    except (ValueError, PermissionError) as e:
        return jsonify({"erro": str(e)}), 400 if isinstance(e, ValueError) else 403


# DASHBOARD


# Retorna estatísticas para o painel do admin
@admin_routes.route("/dashboard", methods=["GET"])
def dashboard_data():
    try:
        verificar_token()
        return jsonify(
            {
                "top_vendidos": get_top_produtos_vendidos(),
                "mais_visualizados": get_produtos_mais_visualizados(),
                "total_vendas_mes": get_total_vendas_periodo(
                    datetime(2025, 8, 1), datetime(2025, 8, 31)
                ),
                "taxa_conversao": get_taxa_conversao(),
            }
        )
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
