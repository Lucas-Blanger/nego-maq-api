import uuid
from database import db
from datetime import datetime

from utils.date_time import agora_brasil


class Produto(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    categoria = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    img = db.Column(db.Text, nullable=True)
    estoque = db.Column(db.Integer, nullable=False, default=0)

    peso = db.Column(db.Numeric(10, 2), nullable=False)  # em kg
    altura = db.Column(db.Integer, nullable=False)  # cm
    largura = db.Column(db.Integer, nullable=False)  # cm
    comprimento = db.Column(db.Integer, nullable=False)  # cm

    criado_em = db.Column(db.DateTime, default=agora_brasil, nullable=False)
    atualizado_em = db.Column(
        db.DateTime,
        default=agora_brasil,
        onupdate=agora_brasil,
        nullable=False,
    )
