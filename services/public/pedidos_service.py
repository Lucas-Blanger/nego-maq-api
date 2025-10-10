from database.models.pedido import Pedido
from database.models.item_pedido import ItemPedido
from database.models.produto import Produto
from database.models.usuario import Usuario
from database.models.endereco import Endereco
from database import db


class PedidoService:

    @staticmethod
    # Cria um novo pedido com itens
    def criar_pedido(data):
        usuario_id = data.get("usuario_id")
        itens = data.get("itens", [])

        if not usuario_id:
            raise ValueError("Usuário não informado")

        if not itens:
            raise ValueError("O pedido precisa ter ao menos um item")

        # Buscar usuário
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        # Puxar o endereço principal do usuário (ou o primeiro disponível)
        endereco = Endereco.query.filter_by(usuario_id=usuario_id).first()
        if not endereco:
            raise ValueError("Usuário não possui endereço cadastrado")

        # Cria o pedido com endereco_id do usuário
        pedido = Pedido(usuario_id=usuario_id, endereco_id=endereco.id, valor_total=0)
        db.session.add(pedido)
        db.session.flush()

        total = 0
        for item in itens:
            produto_id = item.get("produto_id")
            if not produto_id:
                db.session.rollback()
                raise ValueError("Produto não informado em um dos itens")

            produto = Produto.query.get(produto_id)
            if not produto:
                db.session.rollback()
                raise ValueError(f"Produto {produto_id} não encontrado")

            quantidade = item.get("quantidade", 1)
            subtotal = produto.preco * quantidade
            total += subtotal

            db.session.add(
                ItemPedido(
                    pedido_id=pedido.id,
                    produto_id=produto.id,
                    quantidade=quantidade,
                    preco_unitario=produto.preco,
                    peso=produto.peso or 0,
                    comprimento=produto.comprimento or 0,
                    altura=produto.altura or 0,
                    largura=produto.largura or 0,
                )
            )

        pedido.valor_total = total
        db.session.commit()

        return {"pedido_id": pedido.id, "valor_total": float(pedido.valor_total)}

    # Retorna pedido pelo ID
    @staticmethod
    def obter_pedido(pedido_id):
        return Pedido.query.get(pedido_id)

    # Lista todos os pedidos de um usuário
    @staticmethod
    def listar_pedidos_usuario(usuario_id):
        return Pedido.query.filter_by(usuario_id=usuario_id).all()
