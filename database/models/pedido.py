import uuid
from database import db
from sqlalchemy import func
from datetime import datetime, timedelta
from database.enums.status_pedido_enum import StatusPedidoEnum
from utils.date_time import agora_brasil


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
    frete_tipo = db.Column(db.String(50))
    frete_valor = db.Column(db.Numeric(10, 2))
    frete_servico_id = db.Column(db.Integer)
    frete_servico_nome = db.Column(db.String(50))
    criado_em = db.Column(db.DateTime, default=agora_brasil, nullable=False)
    atualizado_em = db.Column(
        db.DateTime,
        default=agora_brasil,
        onupdate=agora_brasil,
        nullable=False,
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
