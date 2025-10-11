import uuid
from database import db
from sqlalchemy.sql import func
from database.enums.status_pedido_enum import StatusPedidoEnum


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = db.Column(
        db.String(36),
        db.ForeignKey("usuario.id", ondelete="CASCADE"),
    )
    endereco_id = db.Column(
        db.String(36), db.ForeignKey("endereco.id", ondelete="CASCADE"), nullable=True
    )
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(
        db.Enum(StatusPedidoEnum), nullable=False, default=StatusPedidoEnum.PENDENTE
    )
    frete_valor = db.Column(db.Numeric(10, 2), nullable=True)
    frete_tipo = db.Column(db.String(50), nullable=True)
    criado_em = db.Column(db.DateTime, server_default=func.now())
    atualizado_em = db.Column(
        db.DateTime, server_default=func.now(), onupdate=func.now()
    )

    melhor_envio_id = db.Column(db.String(100), nullable=True)
    melhor_envio_protocolo = db.Column(db.String(100), nullable=True)
    melhor_envio_rastreio = db.Column(db.String(100), nullable=True)
    etiqueta_url = db.Column(db.Text, nullable=True)

    usuario = db.relationship(
        "Usuario",
        backref=db.backref("pedidos", lazy=True, cascade="all, delete-orphan"),
    )
    endereco = db.relationship(
        "Endereco",
        backref=db.backref("pedidos", lazy=True, cascade="all, delete-orphan"),
    )
