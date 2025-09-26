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
from utils.auth import admin_required

admin_routes = Blueprint("admin", __name__, url_prefix="/admin")


# ROTAS DE PRODUTOS


# Adicionar um novo produto
@admin_routes.route("/produtos", methods=["POST"])
@admin_required
def adicionar_produto_route():
    try:
        file = request.files.get("img")  # se não vier, fica None
        data = {
            "nome": request.form.get("nome"),
            "descricao": request.form.get("descricao"),
            "categoria": request.form.get("categoria"),
            "preco": request.form.get("preco"),
            "estoque": request.form.get("estoque"),
        }

        produto = adicionar_produto_service(data, file)

        return jsonify({"mensagem": "Produto adicionado", "id": produto.id}), 201

    except (ValueError, PermissionError) as e:
        return (
            jsonify({"erro": str(e)}),
            400 if isinstance(e, ValueError) else 403,
        )


# Deletar um produto existente
@admin_routes.route("/produtos/<produto_id>", methods=["DELETE"])
@admin_required
def deletar_produto_route(produto_id):
    try:
        deletar_produto_service(produto_id)
        return jsonify({"mensagem": "Produto removido"}), 200
    except (ValueError, PermissionError) as e:
        return jsonify({"erro": str(e)}), 404 if isinstance(e, ValueError) else 403


# Atualizar os dados de um produto
@admin_routes.route("/produtos/<produto_id>", methods=["PUT"])
@admin_required
def atualizar_produto_route(produto_id):
    try:
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
@admin_required
def atualizar_estoque_route(produto_id):
    try:
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
@admin_routes.route("/produto/promocao/<produto_id>", methods=["POST"])
@admin_required
def criar_promocao_route(produto_id):
    try:
        data = request.json
        criar_promocao_service(produto_id, data.get("desconto_percentual"))
        return jsonify({"mensagem": "Promoção criada com sucesso"}), 201
    except (ValueError, PermissionError) as e:
        return jsonify({"erro": str(e)}), 400 if isinstance(e, ValueError) else 403


# Remover promoção de um produto
@admin_routes.route("/produto/promocao/<produto_id>", methods=["DELETE"])
@admin_required
def remover_promocao_route(produto_id):
    try:
        remover_promocao_service(produto_id)
        return jsonify({"mensagem": "Promoção removida com sucesso"}), 200
    except (ValueError, PermissionError) as e:
        return jsonify({"erro": str(e)}), 400 if isinstance(e, ValueError) else 403


# DASHBOARD


# Retorna estatísticas para o painel do admin
@admin_routes.route("/dashboard", methods=["GET"])
@admin_required
def dashboard_data():
    try:
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
