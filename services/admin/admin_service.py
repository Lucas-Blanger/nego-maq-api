from database import db
from database.models import Produto, Promocao
from sqlalchemy import func
import uuid
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

CATEGORIAS_VALIDAS = ["facas", "aventais", "estojos", "churrascos"]


# PRODUTOS


# Adiciona um novo produto
def adicionar_produto(data, file=None):
    """Adiciona um novo produto ao catálogo"""
    categoria = data.get("categoria")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValueError(
            f"Categoria inválida. Escolha entre: {', '.join(CATEGORIAS_VALIDAS)}"
        )

    obrigatorios = [
        "nome",
        "preco",
        "estoque",
        "peso",
        "altura",
        "largura",
        "comprimento",
    ]
    for campo in obrigatorios:
        if data.get(campo) is None:
            raise ValueError(f"Campo obrigatório '{campo}' não informado.")

    image_url = None
    if file and file.filename != "":
        try:
            upload_result = cloudinary.uploader.upload(file)
            image_url = upload_result["secure_url"]
        except Exception as e:
            raise ValueError(f"Erro ao fazer upload da imagem: {str(e)}")

    produto = Produto(
        id=str(uuid.uuid4()),
        nome=data.get("nome"),
        descricao=data.get("descricao"),
        categoria=categoria,
        preco=data.get("preco"),
        img=image_url,
        estoque=data.get("estoque"),
        peso=data.get("peso"),
        altura=data.get("altura"),
        largura=data.get("largura"),
        comprimento=data.get("comprimento"),
    )
    db.session.add(produto)
    db.session.commit()
    return produto


# Deleta um produto
def deletar_produto(produto_id):
    produto = Produto.query.get(produto_id)
    if not produto:
        raise ValueError("Produto não encontrado")
    db.session.delete(produto)
    db.session.commit()
    return produto


# Atualiza os dados de um produto
def atualizar_produto(produto_id, data):
    produto = Produto.query.get(produto_id)
    if not produto:
        raise ValueError("Produto não encontrado")

    if "categoria" in data and data["categoria"] not in CATEGORIAS_VALIDAS:
        raise ValueError(
            f"Categoria inválida. Escolha entre: {', '.join(CATEGORIAS_VALIDAS)}"
        )

    # Atualiza apenas os campos enviados
    for campo in [
        "nome",
        "descricao",
        "categoria",
        "preco",
        "img",
        "estoque",
        "peso",
        "altura",
        "largura",
        "comprimento",
    ]:
        if campo in data:
            setattr(produto, campo, data[campo])

    db.session.commit()
    return produto


# Atualiza o estoque de um produto
def atualizar_estoque(produto_id, novo_estoque):
    if not isinstance(novo_estoque, int):
        raise ValueError("Estoque inválido")

    produto = Produto.query.get(produto_id)
    if not produto:
        raise ValueError("Produto não encontrado")

    produto.estoque = novo_estoque
    db.session.commit()
    return produto


# PROMOÇÕES


# Cria uma promoção para um produto
def criar_promocao(produto_id, desconto):
    if desconto <= 0:
        raise ValueError("Desconto inválido")

    produto = Produto.query.get(produto_id)
    if not produto:
        raise ValueError("Produto não encontrado")
    if produto.promocao:
        raise ValueError("Esse produto já está em promoção")

    promocao = Promocao(produto_id=produto_id, desconto_percentual=desconto)
    db.session.add(promocao)
    db.session.commit()
    return promocao


# Remove uma promoção
def remover_promocao(produto_id):
    promocao = Promocao.query.filter_by(produto_id=produto_id).first()
    if not promocao:
        raise ValueError("Promoção não encontrada")
    db.session.delete(promocao)
    db.session.commit()
    return promocao
