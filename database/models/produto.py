import uuid
from database import db
from datetime import datetime


class Produto(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    categoria = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    img = db.Column(db.Text, nullable=True)
    estoque = db.Column(db.Integer, nullable=False, default=0)

    peso = db.Column(db.Numeric(10, 2), nullable=False)  # em kg ou gramas
    altura = db.Column(db.Integer, nullable=False)  # cm
    largura = db.Column(db.Integer, nullable=False)  # cm
    comprimento = db.Column(db.Integer, nullable=False)  # cm

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
