from database.models import Promocao
from decimal import Decimal


class PromocaoService:
    # Retorna todas as promoções
    @staticmethod
    def listar():
        return Promocao.query.all()

    # Calcula o preço com desconto
    @staticmethod
    def calcular_preco_com_desconto(preco, desconto_percentual):
        if not preco or not desconto_percentual:
            return preco

        desconto = Decimal(str(desconto_percentual))
        return preco - (preco * desconto / Decimal("100"))
