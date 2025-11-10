from database import db
from database.models import Endereco


# Cria um novo endereço para um usuário
def criar_endereco(usuario_id, data):
    campos_obrigatorios = ["cep", "logradouro", "numero", "bairro", "cidade", "estado"]
    for campo in campos_obrigatorios:
        if campo not in data:
            raise ValueError(f"Campo obrigatório {campo} não informado")

    endereco = Endereco(
        usuario_id=usuario_id,
        cep=data["cep"],
        logradouro=data["logradouro"],
        numero=data["numero"],
        complemento=data.get("complemento"),
        bairro=data["bairro"],
        cidade=data["cidade"],
        estado=data["estado"],
    )
    db.session.add(endereco)
    db.session.commit()
    return endereco


# Edita um endereço existente
def editar_endereco(endereco_id, data):
    endereco = Endereco.query.get(endereco_id)
    if not endereco:
        raise ValueError("Endereço não encontrado")

    campos_editaveis = [
        "cep",
        "logradouro",
        "numero",
        "complemento",
        "bairro",
        "cidade",
        "estado",
    ]
    for campo in campos_editaveis:
        if campo in data:
            setattr(endereco, campo, data[campo])

    db.session.commit()
    return endereco


# Deleta um endereço existente
def deletar_endereco(endereco_id):
    endereco = Endereco.query.get(endereco_id)
    if not endereco:
        raise ValueError("Endereço não encontrado")

    db.session.delete(endereco)
    db.session.commit()


# Lista todos os endereços de um usuário
def listar_enderecos_usuario(usuario_id):
    # Retorna uma lista de endereços de um usuário.
    return Endereco.query.filter_by(usuario_id=usuario_id).all()


# Obtém um endereço pelo ID
def obter_endereco(endereco_id):
    """
    Retorna um endereço específico pelo seu ID.
    """
    return Endereco.query.get(endereco_id)
