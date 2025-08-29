import uuid
from database import db


class Promocao(db.Model):
    __tablename__ = "promocao"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    produto_id = db.Column(db.String(36), db.ForeignKey("produto.id"), nullable=False)
    desconto_percentual = db.Column(db.Float, nullable=False)

    produto = db.relationship("Produto", backref=db.backref("promocao", uselist=False))
