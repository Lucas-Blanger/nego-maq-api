import uuid
from database import db
from sqlalchemy.sql import func
from database.enums.status_pagamento_enum import StatusPagamentoEnum


class TransacaoPagamento(db.Model):
    __tablename__ = "transacao_pagamento"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pedido_id = db.Column(
        db.String(36), db.ForeignKey("pedidos.id", ondelete="CASCADE"), nullable=False
    )
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(
        db.Enum(StatusPagamentoEnum),
        nullable=False,
        default=StatusPagamentoEnum.PENDENTE,
    )
    metodo_pagamento = db.Column(db.String(50), nullable=False)
    mp_payment_id = db.Column(
        db.String(100), nullable=True
    )  # ID do pagamento no Mercado Pago
    mp_preference_id = db.Column(db.String(100), nullable=True)  # ID da preferência
    criado_em = db.Column(db.DateTime, server_default=func.now())
    atualizado_em = db.Column(
        db.DateTime, server_default=func.now(), onupdate=func.now()
    )

    pedido = db.relationship(
        "Pedido",
        backref=db.backref("transacoes", lazy=True, cascade="all, delete-orphan"),
    )
