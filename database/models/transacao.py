import uuid
from database import db
from sqlalchemy.sql import func
from database.enums.status_pagamento_enum import StatusPagamentoEnum


class TransacaoPagamento(db.Model):
    __tablename__ = "transacao_pagamento"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pedido_id = db.Column(db.String(36), db.ForeignKey("pedidos.id"), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(
        db.Enum(StatusPagamentoEnum),
        nullable=False,
        default=StatusPagamentoEnum.PENDENTE,
    )
    metodo_pagamento = db.Column(db.String(50), nullable=False)
    criado_em = db.Column(db.DateTime, server_default=func.now())
    atualizado_em = db.Column(
        db.DateTime, server_default=func.now(), onupdate=func.now()
    )

    pedido = db.relationship("Pedido", backref=db.backref("transacoes", lazy=True))
