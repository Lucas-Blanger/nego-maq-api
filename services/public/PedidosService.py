from venv import logger
from database.enums.status_pedido_enum import StatusPedidoEnum
from database.models.pedido import Pedido
from database.models.item_pedido import ItemPedido
from database.models.produto import Produto
from database.models.usuario import Usuario
from database.models.endereco import Endereco
from database import db
from decimal import Decimal
from services.public.EmailNotificationService import EmailNotificationService


class PedidoService:

    @staticmethod
    # Cria um novo pedido com itens
    def criar_pedido(data):
        usuario_id = data.get("usuario_id")
        endereco_id = data.get("endereco_id")
        itens = data.get("itens", [])
        frete = data.get("frete")

        if not usuario_id:
            raise ValueError("Usuário não informado")
        if not itens:
            raise ValueError("O pedido precisa ter ao menos um item")

        # Buscar usuário
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        # Buscar endereço
        if endereco_id:
            endereco = Endereco.query.get(endereco_id)
            if not endereco:
                raise ValueError("Endereço não encontrado")
            if endereco.usuario_id != usuario_id:
                raise ValueError("Endereço não pertence ao usuário")
        else:
            # Puxar o primeiro endereço do usuário
            endereco = Endereco.query.filter_by(usuario_id=usuario_id).first()
            if not endereco:
                raise ValueError("Usuário não possui endereço cadastrado")

        # Validar frete
        frete_valor = Decimal("0")
        frete_tipo = None
        frete_servico_id = None
        frete_servico_nome = None

        if frete:
            frete_valor = Decimal(str(frete.get("valor", 0)))
            frete_tipo = frete.get("tipo")  # "Jadlog", "Correios"
            frete_servico_id = frete.get("servico_id")  # 3
            frete_servico_nome = frete.get("servico")  # ".Package"

            if frete_valor < 0:
                raise ValueError("Valor do frete inválido")

            # Validar que temos o service_id
            if not frete_servico_id:
                raise ValueError("ID do serviço de frete não informado")

        # Criar o pedido
        pedido = Pedido(
            usuario_id=usuario_id,
            endereco_id=endereco.id,
            valor_total=0,
            frete_valor=frete_valor,
            frete_tipo=frete_tipo,
            frete_servico_id=frete_servico_id,  # ← NOVO
            frete_servico_nome=frete_servico_nome,  # ← NOVO
        )
        db.session.add(pedido)
        db.session.flush()

        # Adicionar itens
        total_produtos = Decimal("0")
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

            # Verificar estoque
            if produto.estoque < quantidade:
                db.session.rollback()
                raise ValueError(
                    f"Estoque insuficiente para o produto {produto.nome}. "
                    f"Disponível: {produto.estoque}, Solicitado: {quantidade}"
                )

            subtotal = produto.preco * quantidade
            total_produtos += subtotal

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

            # Atualizar estoque
            produto.estoque -= quantidade

        # Valor total = produtos + frete
        pedido.valor_total = total_produtos + frete_valor
        db.session.commit()

        try:
            EmailNotificationService.notificar_pedido_criado(pedido)
        except Exception as e:
            logger.error(f"Erro ao enviar email de pedido criado: {e}")

        return {
            "pedido_id": pedido.id,
            "valor_produtos": float(total_produtos),
            "valor_frete": float(frete_valor),
            "valor_total": float(pedido.valor_total),
            "frete_tipo": frete_tipo,
            "frete_servico": frete_servico_nome,
        }

    # Retorna pedido pelo ID
    @staticmethod
    def obter_pedido(pedido_id):
        return Pedido.query.get(pedido_id)

    # Lista todos os pedidos de um usuário
    @staticmethod
    def listar_pedidos_usuario(usuario_id):
        return (
            Pedido.query.filter_by(usuario_id=usuario_id)
            .order_by(Pedido.criado_em.desc())
            .all()
        )

    @staticmethod
    def atualizar_status_pedido(pedido_id, novo_status, codigo_rastreio=None):
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            raise ValueError("Pedido não encontrado")

        status_anterior = pedido.status
        pedido.status = novo_status
        db.session.commit()

        # Enviar notificação de acordo com o novo status
        try:
            if novo_status == StatusPedidoEnum.EM_TRANSITO:
                EmailNotificationService.notificar_pedido_enviado(
                    pedido, codigo_rastreio
                )
            elif novo_status == StatusPedidoEnum.ENTREGUE:
                EmailNotificationService.notificar_pedido_entregue(pedido)
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de status: {e}")

        logger.info(
            f"Status do pedido #{pedido_id} alterado: {status_anterior.value} → {novo_status.value}"
        )

        return pedido
