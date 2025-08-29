from database.models import Produto


class ProdutoService:

    # Retorna todos os produtos

    @staticmethod
    def listar_todos():
        return Produto.query.all()

    # Busca produto pelo ID
    @staticmethod
    def buscar_por_id(produto_id):
        return Produto.query.get(produto_id)

    # Lista produtos com maior estoque (limitado por default a 10)
    @staticmethod
    def listar_top_estoque(limit=10):
        return Produto.query.order_by(Produto.estoque.desc()).limit(limit).all()

    # Busca produtos pelo nome (case-insensitive)
    @staticmethod
    def buscar_por_nome(termo):
        return Produto.query.filter(Produto.nome.ilike(f"%{termo}%")).all()
