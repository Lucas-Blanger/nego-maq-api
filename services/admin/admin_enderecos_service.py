from database import db
from database.models import Endereco


def listar_enderecos():
    # Retorna todos os endereços
    enderecos = Endereco.query.all()
    return [
        {
            "id": e.id,
            "usuario_id": e.usuario_id,
            "cep": e.cep,
            "logradouro": e.logradouro,
            "numero": e.numero,
            "complemento": e.complemento,
            "bairro": e.bairro,
            "cidade": e.cidade,
            "estado": e.estado,
        }
        for e in enderecos
    ]


def atualizar_endereco(endereco_id, data):
    # Atualiza campos de um endereço
    endereco = Endereco.query.get(endereco_id)
    if not endereco:
        raise ValueError("Endereço não encontrado")

    campos = [
        "cep",
        "logradouro",
        "numero",
        "complemento",
        "bairro",
        "cidade",
        "estado",
    ]
    for campo in campos:
        if campo in data:
            setattr(endereco, campo, data[campo])

    db.session.commit()
    return endereco


def deletar_endereco(endereco_id):
    # Deleta um endereço pelo ID
    endereco = Endereco.query.get(endereco_id)
    if not endereco:
        raise ValueError("Endereço não encontrado")

    db.session.delete(endereco)
    db.session.commit()
    return endereco
