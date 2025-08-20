import uuid
from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.sql import func


class Produto(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    categoria = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    img = db.Column(db.Text, nullable=True)
    estoque = db.Column(db.Integer, nullable=False, default=0)


class Usuario(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(15), nullable=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def checar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


class Evento(db.Model):
    __tablename__ = "evento"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.String(36), db.ForeignKey("usuario.id"), nullable=True)
    produto_id = db.Column(db.String(36), db.ForeignKey("produto.id"), nullable=True)
    tipo_evento = db.Column(db.String(50), nullable=True)
    valor = db.Column(db.Numeric(10, 2), nullable=True)
    data_evento = db.Column(db.DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Evento {self.tipo_evento} - Produto {self.produto_id}>"
