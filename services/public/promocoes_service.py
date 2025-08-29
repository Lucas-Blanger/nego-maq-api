from database.models import Promocao


class PromocaoService:

    # Retorna todas as promoções
    @staticmethod
    def listar():
        return Promocao.query.all()
