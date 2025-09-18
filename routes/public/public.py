from flask import Blueprint, request, jsonify
from services.public.produtos_service import ProdutoService
from services.public.carrinho_service import CarrinhoService
from services.public.promocoes_service import PromocaoService
from utils.auth import token_required


public_routes = Blueprint("public", __name__)


# Health check
@public_routes.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "API está funcionando corretamente"})


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
            }
            for p in produtos
        ]
    )


# CARRINHO DE COMPRAS


# Adiciona um produto ao carrinho
@public_routes.route("/carrinho/adicionar/<string:produto_id>", methods=["POST"])
@token_required
def adicionar_ao_carrinho(payload, produto_id):
    usuario_id = payload["id"]
    try:
        carrinho = CarrinhoService.adicionar(usuario_id, produto_id)
        return jsonify(
            {
                "mensagem": "Produto adicionado",
                "carrinho": [
                    {"nome": p.nome, "preco": float(p.preco)} for p in carrinho
                ],
            }
        )
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


# Finaliza a compra (gera link do WhatsApp)
@public_routes.route("/finalizar", methods=["GET"])
@token_required
def finalizar_compra(payload):
    usuario_id = payload["id"]
    try:
        link = CarrinhoService.finalizar(usuario_id)
        return jsonify({"whatsapp_url": link})
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


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
                    p.produto.preco - (p.produto.preco * (p.desconto_percentual / 100)),
                    2,
                ),
            }
            for p in promocoes
        ]
    )
