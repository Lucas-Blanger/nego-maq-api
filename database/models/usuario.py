import uuid
from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import os


fernet = Fernet(os.getenv("SECRET_KEY_FERNET"))


class Usuario(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(15), nullable=True)
    _cpf = db.Column("cpf", db.String(255), nullable=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def checar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def cpf(self):
        if not self._cpf:
            return None
        try:
            return fernet.decrypt(self._cpf.encode()).decode()
        except Exception:
            return None

    @cpf.setter
    def cpf(self, valor):
        valor_limpo = "".join(filter(str.isdigit, valor))
        self._cpf = fernet.encrypt(valor_limpo.encode()).decode()
