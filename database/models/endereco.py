import uuid
from database import db


class Endereco(db.Model):
    __tablename__ = "endereco"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = db.Column(db.String(36), db.ForeignKey("usuario.id"), nullable=False)
    cep = db.Column(db.String(9), nullable=False)
    logradouro = db.Column(db.String(255), nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    complemento = db.Column(db.String(100), nullable=True)
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)

    usuario = db.relationship(
        "Usuario",
        backref=db.backref(
            "enderecos",
            lazy=True,
            cascade="all, delete-orphan",
            passive_deletes=True,
        ),
    )
