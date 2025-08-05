from flask import Blueprint, request, jsonify
from database.models import Produto

public_routes = Blueprint("public", __name__)

carrinho = []


# health api
@public_routes.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "API está funcionando corretamente"})


# listar todos os produtos
@public_routes.route("/produtos", methods=["GET"])
def listar_produtos():
    produtos = Produto.query.all()
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


# listar produto por id
@public_routes.route("/produtos/<string:id>", methods=["GET"])
def buscar_produto_por_id(id):
    produto = Produto.query.get(id)
    if produto:
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
    else:
        return jsonify({"erro": "Produto não encontrado"}), 404


# listar adicionar no carrinho
@public_routes.route("/carrinho/adicionar/<string:produto_id>", methods=["POST"])
def adicionar_ao_carrinho(produto_id):
    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    carrinho.append(produto)
    return jsonify(
        {
            "mensagem": "Produto adicionado",
            "carrinho": [{"nome": p.nome, "preco": float(p.preco)} for p in carrinho],
        }
    )


# finalizar compra
@public_routes.route("/finalizar", methods=["GET"])
def finalizar_compra():
    if not carrinho:
        return jsonify({"erro": "Carrinho vazio"}), 400

    mensagem = "Olá! Quero comprar:\n"
    for p in carrinho:
        mensagem += f"- {p.nome} (R${p.preco})\n"

    carrinho.clear()
    link = f"https://wa.me/555492205166?text={mensagem.replace(' ', '%20')}"
    return jsonify({"whatsapp_url": link})


# listar produto por nome
@public_routes.route("/produtos/busca", methods=["GET"])
def buscar_produtos_por_nome():
    termo = request.args.get("nome", "").strip()
    if not termo:
        return jsonify({"erro": "Informe um termo para busca"}), 400

    produtos = Produto.query.filter(Produto.nome.ilike(f"%{termo}%")).all()
    resultados = [
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

    return jsonify(resultados)
