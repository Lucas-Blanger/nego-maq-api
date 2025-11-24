from flask import Blueprint, request, jsonify
from services.public.ProdutosServices import ProdutoService
from services.public.PromocoesService import PromocaoService
from utils.middlewares.auth import token_required


public_routes = Blueprint("public", __name__)


# Health check
@public_routes.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "API está funcionando corretamente", "version": "2.0.1"})


# PRODUTOS


# Lista todos os produtos disponíveis
@public_routes.route("/produtos", methods=["GET"])
def listar_produtos():
    produtos = ProdutoService.listar_todos()
    return jsonify(
        [
            {
                "id": p.id,
                "nome": p.nome,
                "descricao": p.descricao,
                "categoria": p.categoria,
                "preco": float(p.preco),
                "img": p.img,
                "estoque": p.estoque,
                "peso": float(p.peso),
                "altura": p.altura,
                "largura": p.largura,
                "comprimento": p.comprimento,
            }
            for p in produtos
        ]
    )


# Busca um produto específico pelo ID
@public_routes.route("/produtos/<string:id>", methods=["GET"])
def buscar_produto_por_id(id):
    produto = ProdutoService.buscar_por_id(id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    return jsonify(
        {
            "id": produto.id,
            "nome": produto.nome,
            "descricao": produto.descricao,
            "categoria": produto.categoria,
            "preco": float(produto.preco),
            "img": produto.img,
            "estoque": int(produto.estoque),
            "peso": float(produto.peso),
            "altura": produto.altura,
            "largura": produto.largura,
            "comprimento": produto.comprimento,
        }
    )


# Lista os 5 produtos com maior estoque (para a página inicial)
@public_routes.route("/produtos/home", methods=["GET"])
def listar_top_estoque():
    produtos = ProdutoService.listar_top_estoque()
    return jsonify(
        [
            {
                "id": p.id,
                "nome": p.nome,
                "descricao": p.descricao,
                "categoria": p.categoria,
                "preco": float(p.preco),
                "img": p.img,
                "estoque": p.estoque,
                "peso": float(p.peso),
                "altura": p.altura,
                "largura": p.largura,
                "comprimento": p.comprimento,
            }
            for p in produtos
        ]
    )


# Lista os 5 últimos produtos adicionados
@public_routes.route("/produtos/novidades", methods=["GET"])
def listar_ultimos_produtos_adicionados():
    produtos = ProdutoService.listar_ultimos_adicionados()
    if not produtos:
        return jsonify({"mensagem": "Nenhum produto encontrado"}), 404

    return jsonify(
        [
            {
                "id": p.id,
                "nome": p.nome,
                "descricao": p.descricao,
                "categoria": p.categoria,
                "preco": float(p.preco),
                "img": p.img,
                "estoque": p.estoque,
                "peso": float(p.peso),
                "altura": p.altura,
                "largura": p.largura,
                "comprimento": p.comprimento,
            }
            for p in produtos
        ]
    )


# Busca produtos pelo nome (usando query param ?nome=)
@public_routes.route("/produtos/busca", methods=["GET"])
def buscar_produtos_por_nome():
    termo = request.args.get("nome", "").strip()
    if not termo:
        return jsonify({"erro": "Informe um termo para busca"}), 400

    produtos = ProdutoService.buscar_por_nome(termo)
    return jsonify(
        [
            {
                "id": p.id,
                "nome": p.nome,
                "descricao": p.descricao,
                "categoria": p.categoria,
                "preco": float(p.preco),
                "img": p.img,
                "estoque": p.estoque,
                "peso": float(p.peso),
                "altura": p.altura,
                "largura": p.largura,
                "comprimento": p.comprimento,
            }
            for p in produtos
        ]
    )


# PROMOÇÕES


# Lista promoções ativas (com preço já calculado com desconto)
@public_routes.route("/promocoes", methods=["GET"])
def listar_promocoes():
    promocoes = PromocaoService.listar()
    return jsonify(
        [
            {
                "id": p.id,
                "produto_id": p.produto_id,
                "produto_nome": p.produto.nome,
                "preco_original": float(p.produto.preco),
                "desconto_percentual": p.desconto_percentual,
                "preco_com_desconto": round(
                    float(
                        PromocaoService.calcular_preco_com_desconto(
                            p.produto.preco, p.desconto_percentual
                        )
                    ),
                    2,
                ),
            }
            for p in promocoes
        ]
    )
