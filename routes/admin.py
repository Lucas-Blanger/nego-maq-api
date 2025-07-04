from flask import Blueprint, request, jsonify
from database.models import Produto
from database import db
from config import ADMIN_TOKEN
import uuid

admin_routes = Blueprint('admin', __name__, url_prefix='/admin')

@admin_routes.route('/produtos', methods=['POST'])
def adicionar_produto():
    token = request.headers.get('Authorization')
    if token != ADMIN_TOKEN:
        return jsonify({"erro": "Não autorizado"}), 403

    data = request.json
    categorias_validas = ['facas', 'aventais', 'estojos', 'churrascos']
    categoria = data.get('categoria')

    if categoria not in categorias_validas:
        return jsonify({"erro": f"Categoria inválida. Escolha entre: {', '.join(categorias_validas)}"}), 400

    novo = Produto(
        id=str(uuid.uuid4()),
        nome=data.get('nome'),
        descricao=data.get('descricao'),
        categoria=categoria,
        preco=data.get('preco'),
        img=data.get('img'),
        estoque=data.get('estoque')
    )
    db.session.add(novo)
    db.session.commit()
    return jsonify({"mensagem": "Produto adicionado", "id": novo.id}), 201


@admin_routes.route('/produtos/<produto_id>', methods=['DELETE'])
def deletar_produto(produto_id):
    token = request.headers.get('Authorization')
    if token != ADMIN_TOKEN:
        return jsonify({"erro": "Não autorizado"}), 403

    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    db.session.delete(produto)
    db.session.commit()
    return jsonify({"mensagem": "Produto removido"}), 200


@admin_routes.route('/estoque/<produto_id>', methods=['PUT'])
def atualizar_estoque(produto_id):
    token = request.headers.get('Authorization')
    if token != ADMIN_TOKEN:
        return jsonify({"erro": "Não autorizado"}), 403

    data = request.get_json()
    novo_estoque = data.get('estoque')

    if novo_estoque is None or type(novo_estoque) is not int:
        return jsonify({"erro": "Estoque inválido"}), 400

    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    produto.estoque = novo_estoque
    db.session.commit()

    return jsonify({"mensagem": "Estoque atualizado", "produto_id": produto.id, "estoque": produto.estoque}), 200
