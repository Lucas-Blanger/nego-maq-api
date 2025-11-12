from database.models import usuario
from utils.crypto_utils import descriptografar_cpf


class UserFormatter:
    @staticmethod
    def formatar_dados_usuario(usuario):
        tem_endereco = False

        enderecos = []

        if hasattr(usuario, "enderecos") and usuario.enderecos:
            tem_endereco = len(usuario.enderecos) > 0
            enderecos = [
                {
                    "id": e.id,
                    "cep": e.cep,
                    "logradouro": e.logradouro,
                    "numero": e.numero,
                    "complemento": e.complemento,
                    "bairro": e.bairro,
                    "cidade": e.cidade,
                    "estado": e.estado,
                }
                for e in usuario.enderecos
            ]

        return {
            "id": usuario.id,
            "nome": usuario.nome,
            "sobrenome": usuario.sobrenome,
            "email": usuario.email,
            "telefone": usuario.telefone,
            "cpf": descriptografar_cpf(usuario.cpf) if usuario.cpf else None,
            "is_admin": usuario.is_admin,
            "tem_endereco": tem_endereco,
            "enderecos": enderecos,
        }


formatar_dados_usuario = UserFormatter.formatar_dados_usuario
__all__ = ["formatar_dados_usuario"]
