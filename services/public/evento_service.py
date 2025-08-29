from database import db
from database.models import Evento, Produto
from sqlalchemy import func


# Registra um evento no banco de dados
def registrar_evento(usuario_id, produto_id, tipo_evento):
    """Registra um evento no banco de dados"""
    evento = Evento(
        usuario_id=usuario_id, produto_id=produto_id, tipo_evento=tipo_evento
    )
    db.session.add(evento)
    db.session.commit()
    return evento


# Retorna os produtos mais vendidos
def top_vendas(limit=3):
    """Retorna os produtos mais vendidos"""
    resultados = (
        db.session.query(Evento.produto_id, func.count(Evento.id).label("total_vendas"))
        .filter(Evento.tipo_evento == "compra")
        .group_by(Evento.produto_id)
        .order_by(func.count(Evento.id).desc())
        .limit(limit)
        .all()
    )
    return [
        {"produto_id": r.produto_id, "total_vendas": r.total_vendas} for r in resultados
    ]


# Retorna produtos recomendados por categoria e vendas
def recomendacoes(produto_id, limit=5):
    # Retorna produtos similares por categoria, ordenados por vendas
    produto = Produto.query.get(produto_id)
    if not produto:
        return []

    similares = (
        db.session.query(
            Produto.id, Produto.nome, func.count(Evento.id).label("vendas")
        )
        .join(Evento, Evento.produto_id == Produto.id)
        .filter(
            Produto.categoria == produto.categoria,  # Mesma categoria
            Produto.id != produto_id,  # Exclui o produto atual
            Evento.tipo_evento == "compra",  # Apenas compras
        )
        .group_by(Produto.id)
        .order_by(func.count(Evento.id).desc())  # Ordena por vendas
        .limit(limit)
        .all()
    )

    return [{"id": p.id, "nome": p.nome, "vendas": p.vendas} for p in similares]
