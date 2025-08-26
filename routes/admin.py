from flask import Blueprint, request, jsonify
from database.models import Produto, Evento, Promocao
from database import db
from config import ADMIN_TOKEN
import uuid
from sqlalchemy import func
from datetime import datetime

admin_routes = Blueprint("admin", __name__, url_prefix="/admin")


# ROTAS DE GESTÃO DE PRODUTOS
@admin_routes.route("/produtos", methods=["POST"])

# Adiciona um novo produto ao catálogo.
# Requer token de autorização de administrador (ADMIN_TOKEN).
def adicionar_produto():
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    if token != ADMIN_TOKEN:
        return jsonify({"erro": "Não autorizado"}), 403

    data = request.json
    categorias_validas = ["facas", "aventais", "estojos", "churrascos"]
    categoria = data.get("categoria")

    # Verifica se a categoria é válida
    if categoria not in categorias_validas:
        return (
            jsonify(
                {
                    "erro": f"Categoria inválida. Escolha entre: {', '.join(categorias_validas)}"
                }
            ),
            400,
        )

    novo = Produto(
        id=str(uuid.uuid4()),
        nome=data.get("nome"),
        descricao=data.get("descricao"),
        categoria=categoria,
        preco=data.get("preco"),
        img=data.get("img"),
        estoque=data.get("estoque"),
    )
    db.session.add(novo)
    db.session.commit()
    return jsonify({"mensagem": "Produto adicionado", "id": novo.id}), 201


@admin_routes.route("/produtos/<produto_id>", methods=["DELETE"])
# Remove um produto do catálogo pelo ID.
def deletar_produto(produto_id):
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    if token != ADMIN_TOKEN:
        return jsonify({"erro": "Não autorizado"}), 403

    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    db.session.delete(produto)
    db.session.commit()
    return jsonify({"mensagem": "Produto removido"}), 200


@admin_routes.route("/estoque/<produto_id>", methods=["PUT"])
# Atualiza o estoque de um produto específico.
def atualizar_estoque(produto_id):
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    if token != ADMIN_TOKEN:
        return jsonify({"erro": "Não autorizado"}), 403

    data = request.get_json()
    novo_estoque = data.get("estoque")

    if novo_estoque is None or type(novo_estoque) is not int:
        return jsonify({"erro": "Estoque inválido"}), 400

    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    produto.estoque = novo_estoque
    db.session.commit()

    return (
        jsonify(
            {
                "mensagem": "Estoque atualizado",
                "produto_id": produto.id,
                "estoque": produto.estoque,
            }
        ),
        200,
    )


@admin_routes.route("/produtos/<produto_id>", methods=["PUT"])
# Atualiza o produto pelo ID.
def atualizar_produto(produto_id):
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    if token != ADMIN_TOKEN:
        return jsonify({"erro": "Não autorizado"}), 403

    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    data = request.get_json()
    categorias_validas = ["facas", "aventais", "estojos", "churrascos"]

    if "categoria" in data and data["categoria"] not in categorias_validas:
        return (
            jsonify(
                {
                    "erro": f"Categoria inválida. Escolha entre: {', '.join(categorias_validas)}"
                }
            ),
            400,
        )

    # Atualiza apenas os campos enviados
    if "nome" in data:
        produto.nome = data["nome"]
    if "descricao" in data:
        produto.descricao = data["descricao"]
    if "categoria" in data:
        produto.categoria = data["categoria"]
    if "preco" in data:
        produto.preco = data["preco"]
    if "img" in data:
        produto.img = data["img"]
    if "estoque" in data:
        produto.estoque = data["estoque"]

    db.session.commit()
    return (
        jsonify({"mensagem": "Produto atualizado com sucesso", "produto": produto.id}),
        200,
    )

# Criar promoção
@admin_routes.route('produto/promocao/<int:produto_id>', methods=['POST'])
def criar_promocao(produto_id):
    data = request.get_json()
    desconto = data.get('desconto_percentual')

    if desconto is None or desconto <= 0:
        return jsonify({'erro': 'Desconto inválido'}), 400

    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({'erro': 'Produto não encontrado'}), 404

    # Verifica se já existe promoção para esse produto
    if produto.promocao:
        return jsonify({'erro': 'Esse produto já está em promoção'}), 400

    promocao = Promocao(produto_id=produto_id, desconto_percentual=desconto)

    db.session.add(promocao)
    db.session.commit()

    return jsonify({'mensagem': 'Promoção criada com sucesso'}), 201


# Remover promoção (pelo produto)
@admin_routes.route('produto/promocao/<int:produto_id>', methods=['DELETE'])
def remover_promocao(produto_id):
    promocao = Promocao.query.filter_by(produto_id=produto_id).first()
    if not promocao:
        return jsonify({'erro': 'Promoção não encontrada'}), 404

    db.session.delete(promocao)
    db.session.commit()

    return jsonify({'mensagem': 'Promoção removida com sucesso'}), 200



# FUNÇÕES DE RELATÓRIOS
def get_top_produtos_vendidos(limit=5):
    # Retorna os produtos mais vendidos (baseado em eventos de 'compra'),
    resultados = (
        db.session.query(
            Produto.nome,
            func.count(Evento.id).label("vendas"),
            func.sum(Produto.preco).label("receita"),
        )
        .join(Produto, Produto.id == Evento.produto_id)
        .filter(Evento.tipo_evento == "compra")
        .group_by(Produto.id)
        .order_by(func.count(Evento.id).desc())
        .limit(limit)
        .all()
    )
    return [dict(nome=r[0], vendas=r[1], receita=float(r[2])) for r in resultados]


def get_produtos_mais_visualizados(limit=5):
    # Retorna os produtos mais visualizados (baseado em eventos de 'visualizacao').
    resultados = (
        db.session.query(Produto.nome, func.count(Evento.id).label("visualizacoes"))
        .join(Produto, Produto.id == Evento.produto_id)
        .filter(Evento.tipo_evento == "visualizacao")
        .group_by(Produto.id)
        .order_by(func.count(Evento.id).desc())
        .limit(limit)
        .all()
    )
    return [dict(nome=r[0], visualizacoes=r[1]) for r in resultados]


def get_total_vendas_periodo(inicio, fim):
    #   Retorna o total de vendas em um período específico.
    total = (
        db.session.query(func.count(Evento.id))
        .filter(Evento.tipo_evento == "compra")
        .filter(Evento.data_evento >= inicio, Evento.data_evento <= fim)
        .scalar()
    )
    return total


def get_taxa_conversao():
    #    Calcula a taxa de conversão:
    # (número de compras / número de visualizações) * 100
    visualizacoes = (
        db.session.query(func.count(Evento.id))
        .filter(Evento.tipo_evento == "visualizacao")
        .scalar()
    )
    compras = (
        db.session.query(func.count(Evento.id))
        .filter(Evento.tipo_evento == "compra")
        .scalar()
    )

    if visualizacoes == 0:
        return 0
    return round((compras / visualizacoes) * 100, 2)


@admin_routes.route("/dashboard", methods=["GET"])
# Retorna dados agregados para o painel admin:
# - Produtos mais vendidos
# - Produtos mais visualizados
# - Total de vendas no mês (exemplo: agosto 2025)
# - Taxa de conversão
def dashboard_data():
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
