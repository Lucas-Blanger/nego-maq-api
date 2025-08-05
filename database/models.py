import uuid
from database import db
from werkzeug.security import generate_password_hash, check_password_hash


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
    senha_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def checar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
