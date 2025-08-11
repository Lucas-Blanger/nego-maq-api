from flask import Blueprint, request, jsonify
from database.models import Evento, Produto
from database import db
import uuid

event_routes = Blueprint("events", __name__, url_prefix="/eventos")


@event_routes.route("/registrar_evento", methods=["POST"])
def registrar_evento():
    dados = request.json

    evento = Evento(
        usuario_id=dados.get("usuario_id"),
        produto_id=dados.get("produto_id"),
        tipo_evento=dados.get("tipo_evento"),
    )

    db.session.add(evento)
    db.session.commit()

    return jsonify({"mensagem": "Evento registrado com sucesso!"}), 201


@event_routes.route("/analise/top_vendas", methods=["GET"])
def top_vendas():
    from sqlalchemy import func

    resultados = (
        db.session.query(Evento.produto_id, func.count(Evento.id).label("total_vendas"))
        .filter(Evento.tipo_evento == "compra")
        .group_by(Evento.produto_id)
        .order_by(func.count(Evento.id).desc())
        .limit(3)
        .all()
    )

    return jsonify(
        [
            {"produto_id": r.produto_id, "total_vendas": r.total_vendas}
            for r in resultados
        ]
    )


@event_routes.route("/recomendacoes/<int:produto_id>", methods=["GET"])
def recomendacoes(produto_id):
    # Busca categoria do produto
    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify([])

    # Sugere outros produtos da mesma categoria, ordenados por vendas
    from sqlalchemy import func

    similares = (
        db.session.query(
            Produto.id, Produto.nome, func.count(Evento.id).label("vendas")
        )
        .join(Evento, Evento.produto_id == Produto.id)
        .filter(
            Produto.categoria_id == produto.categoria_id,
            Produto.id != produto_id,
            Evento.tipo_evento == "compra",
        )
        .group_by(Produto.id)
        .order_by(func.count(Evento.id).desc())
        .limit(5)
        .all()
    )

    return jsonify(
        [{"id": p.id, "nome": p.nome, "vendas": p.vendas} for p in similares]
    )
