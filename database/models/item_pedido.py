import uuid
from database import db


class ItemPedido(db.Model):
    __tablename__ = "itens_pedido"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    pedido_id = db.Column(
        db.String(36), db.ForeignKey("pedidos.id", ondelete="CASCADE"), nullable=False
    )

    produto_id = db.Column(db.String(36), db.ForeignKey("produto.id"), nullable=False)

    quantidade = db.Column(db.Integer, nullable=False, default=1)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    # Campos de frete
    peso = db.Column(db.Numeric(10, 2), nullable=False)
    comprimento = db.Column(db.Numeric(10, 2), nullable=False)
    altura = db.Column(db.Numeric(10, 2), nullable=False)
    largura = db.Column(db.Numeric(10, 2), nullable=False)

    pedido = db.relationship("Pedido", back_populates="itens")
    produto = db.relationship("Produto", back_populates="itens_pedido")
