import uuid
from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.sql import func
import enum


class Produto(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
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

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = db.Column(db.String(36), db.ForeignKey("usuario.id"), nullable=True)
    produto_id = db.Column(db.String(36), db.ForeignKey("produto.id"), nullable=True)
    tipo_evento = db.Column(db.String(50), nullable=True)
    valor = db.Column(db.Numeric(10, 2), nullable=True)
    data_evento = db.Column(db.DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Evento {self.tipo_evento} - Produto {self.produto_id}>"


class Promocao(db.Model):
    __tablename__ = "promocao"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    produto_id = db.Column(db.String(36), db.ForeignKey("produto.id"), nullable=False)
    desconto_percentual = db.Column(db.Float, nullable=False)

    produto = db.relationship("Produto", backref=db.backref("promocao", uselist=False))


class StatusPedidoEnum(enum.Enum):
    PENDENTE = "Pendente"
    PAGO = "Pago"
    ENVIADO = "Enviado"
    ENTREGUE = "Entregue"
    CANCELADO = "Cancelado"


class StatusPagamentoEnum(enum.Enum):
    PENDENTE = "Pendente"
    APROVADO = "Aprovado"
    RECUSADO = "Recusado"
    ESTORNADO = "Estornado"


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = db.Column(db.String(36), db.ForeignKey("usuario.id"), nullable=True)
    endereco_id = db.Column(db.String(36), db.ForeignKey("endereco.id"), nullable=True)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(
        db.Enum(StatusPedidoEnum), nullable=False, default=StatusPedidoEnum.PENDENTE
    )
    frete_valor = db.Column(db.Numeric(10, 2), nullable=True)
    frete_tipo = db.Column(db.String(50), nullable=True)
    criado_em = db.Column(db.DateTime, server_default=func.now())
    atualizado_em = db.Column(
        db.DateTime, server_default=func.now(), onupdate=func.now()
    )

    usuario = db.relationship("Usuario", backref=db.backref("pedidos", lazy=True))
    endereco = db.relationship("Endereco", backref=db.backref("pedidos", lazy=True))


class ItemPedido(db.Model):
    __tablename__ = "itens_pedido"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pedido_id = db.Column(db.String(36), db.ForeignKey("pedidos.id"), nullable=False)
    produto_id = db.Column(db.String(36), db.ForeignKey("produto.id"), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    pedido = db.relationship("Pedido", backref=db.backref("itens", lazy=True))
    produto = db.relationship("Produto", backref=db.backref("itens_pedido", lazy=True))


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

    usuario = db.relationship("Usuario", backref=db.backref("enderecos", lazy=True))
