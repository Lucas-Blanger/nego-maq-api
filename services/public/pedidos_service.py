from database.models.pedido import Pedido
from database.models.item_pedido import ItemPedido
from database.models.produto import Produto
from database import db


class PedidoService:

    @staticmethod
    # Cria um novo pedido com itens
    def criar_pedido(data):
        usuario_id = data.get("usuario_id")
        endereco_id = data.get("endereco_id")
        itens = data.get("itens", [])

        if not itens:
            raise ValueError("O pedido precisa ter ao menos um item")

        # Cria o pedido já com endereco_id
        pedido = Pedido(usuario_id=usuario_id, endereco_id=endereco_id, valor_total=0)
        db.session.add(pedido)
        db.session.flush()

        total = 0
        for item in itens:
            produto = Produto.query.get(item["produto_id"])
            if not produto:
                db.session.rollback()
                raise ValueError(f"Produto {item['produto_id']} não encontrado")

            quantidade = item.get("quantidade", 1)
            subtotal = produto.preco * quantidade
            total += subtotal

            db.session.add(
                ItemPedido(
                    pedido_id=pedido.id,
                    produto_id=produto.id,
                    quantidade=quantidade,
                    preco_unitario=produto.preco,
                    peso=item.get("peso", 0),
                    comprimento=item.get("comprimento", 0),
                    altura=item.get("altura", 0),
                    largura=item.get("largura", 0),
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
