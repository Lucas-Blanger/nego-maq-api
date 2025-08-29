import uuid
from database import db
from sqlalchemy.sql import func


class Evento(db.Model):
    __tablename__ = "evento"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = db.Column(db.String(36), db.ForeignKey("usuario.id"), nullable=True)
    produto_id = db.Column(db.String(36), db.ForeignKey("produto.id"), nullable=True)
    tipo_evento = db.Column(db.String(50), nullable=True)
    valor = db.Column(db.Numeric(10, 2), nullable=True)
    data_evento = db.Column(db.DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Evento {self.tipo_evento} - Produto {self.produto_id}>"
