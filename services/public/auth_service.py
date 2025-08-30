from database import db
from database.models import Usuario


# Registra um novo usuário
def registrar(nome, sobrenome, email, telefone, senha, is_admin=False):
    """Registra um novo usuário"""
    if Usuario.query.filter_by(email=email).first():
        raise ValueError("Email já cadastrado")

    usuario = Usuario(
        nome=nome,
        sobrenome=sobrenome,
        email=email,
        telefone=telefone,
        is_admin=is_admin,
    )
    usuario.set_senha(senha)
    db.session.add(usuario)
    db.session.commit()
    return usuario


# Faz login do usuário
def login(email, senha):
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario and usuario.checar_senha(senha):
        return usuario
    raise ValueError("Credenciais inválidas")


# Recupera/Atualiza a senha do usuário
def recuperar_senha(email, nova_senha):

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        raise ValueError("Usuário não encontrado")

    usuario.set_senha(nova_senha)
    db.session.commit()
    return usuario


# Edita o perfil do usuário
def editar_perfil(
    email_atual,
    nome=None,
    novo_sobrenome=None,
    novo_email=None,
    novo_telefone=None,
    nova_senha=None,
):
    """Atualiza dados do usuário"""
    usuario = Usuario.query.filter_by(email=email_atual).first()
    if not usuario:
        raise ValueError("Usuário não encontrado")

    if nome:
        usuario.nome = nome

    if novo_sobrenome:
        usuario.sobrenome = novo_sobrenome

    if novo_email:
        if Usuario.query.filter_by(email=novo_email).first():
            raise ValueError("Novo email já está em uso")
        usuario.email = novo_email

    if novo_telefone:
        usuario.telefone = novo_telefone

    if nova_senha:
        usuario.set_senha(nova_senha)

    db.session.commit()
    return usuario
