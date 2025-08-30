from flask import Flask, request, jsonify, Blueprint
from services.public.pedidos_service import PedidoService
from services.public.pagamentos_service import PagamentoService

app = Flask(__name__)
public_routes_pedidos = Blueprint("pedidos_public", __name__)


# PEDIDOS PÚBLICOS


# CRIAR UM NOVO PEDIDO
@public_routes_pedidos.route("/pedidos", methods=["POST"])
def criar_pedido():
    """
    Cria um novo pedido.
    Espera JSON com os dados do pedido (ex.: usuário, produtos, quantidades, valores).
    Retorna o pedido criado em formato JSON.
    """
    try:
        data = request.json
        pedido = PedidoService.criar_pedido(data)
        return jsonify(pedido), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


# Resumo do pedido para frete
@public_routes_pedidos.route("/pedidos/<pedido_id>/frete/resumo", methods=["GET"])
def resumo_frete(pedido_id):
    """
    Retorna os dados do pedido necessários para calcular frete:
    - Peso total
    - Dimensões (comprimento, altura, largura) de cada item
    """
    pedido = PedidoService.obter_pedido(pedido_id)
    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    itens = [
        {
            "produto_id": i.produto_id,
            "quantidade": i.quantidade,
            "peso": float(i.peso),
            "comprimento": float(i.comprimento),
            "altura": float(i.altura),
            "largura": float(i.largura),
        }
        for i in pedido.itens
    ]

    # Somar peso total para facilitar a cotação
    peso_total = sum(i["peso"] * i["quantidade"] for i in itens)

    return jsonify(
        {
            "pedido_id": pedido.id,
            "cep_origem": pedido.endereco.cep,
            "itens": itens,
            "peso_total": peso_total,
        }
    )


# Calcular cotação de frete via
@public_routes_pedidos.route("/pedidos/<pedido_id>/frete/cotacao", methods=["POST"])
def cotacao_frete(pedido_id):
    """
    Recebe JSON com:
    {
        "cep_destino": "12345678"
    }
    Retorna dados formatados
    """
    data = request.json
    cep_destino = data.get("cep_destino")
    if not cep_destino:
        return jsonify({"erro": "cep_destino é obrigatório"}), 400

    pedido = PedidoService.obter_pedido(pedido_id)
    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    # Preparar itens para cálculo de frete
    itens = [
        {
            "peso": float(i.peso),
            "comprimento": float(i.comprimento),
            "altura": float(i.altura),
            "largura": float(i.largura),
            "quantidade": i.quantidade,
        }
        for i in pedido.itens
    ]

    frete_data = {
        "cep_origem": pedido.cep_origem,
        "cep_destino": cep_destino,
        "itens": itens,
    }

    return jsonify(frete_data), 200


# Obter pedido
@public_routes_pedidos.route("/pedidos/<pedido_id>", methods=["GET"])
def obter_pedido(pedido_id):
    """
    Busca um pedido específico pelo ID.
    Retorna os dados completos do pedido, incluindo:
    - Informações principais
    - Itens do pedido
    - Transações associadas
    """
    pedido = PedidoService.obter_pedido(pedido_id)
    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    return jsonify(
        {
            "pedido_id": pedido.id,
            "usuario_id": pedido.usuario_id,
            "valor_total": float(pedido.valor_total),
            "status": pedido.status.value,
            "itens": [
                {
                    "produto_id": i.produto_id,
                    "quantidade": i.quantidade,
                    "preco_unitario": float(i.preco_unitario),
                }
                for i in pedido.itens
            ],
            "transacoes": [
                {
                    "id": t.id,
                    "valor": float(t.valor),
                    "status": t.status.value,
                    "metodo_pagamento": t.metodo_pagamento,
                }
                for t in pedido.transacoes
            ],
        }
    )


# Pedidos por usuário
@public_routes_pedidos.route("/usuarios/<usuario_id>/pedidos", methods=["GET"])
def pedidos_usuario(usuario_id):
    # Lista todos os pedidos de um usuário específico. Retorna apenas informações resumidas (id, valor total, status).

    pedidos = PedidoService.listar_pedidos_usuario(usuario_id)
    return jsonify(
        [
            {
                "pedido_id": p.id,
                "valor_total": float(p.valor_total),
                "status": p.status.value,
            }
            for p in pedidos
        ]
    )


# Criar transação
@public_routes_pedidos.route("/pedidos/<pedido_id>/transacoes", methods=["POST"])
def criar_transacao(pedido_id):
    """
     #Cria uma nova transação (pagamento) vinculada a um pedido.
    Espera JSON com:
    {
        "valor": <valor da transação>,
        "metodo_pagamento": <ex.: "pix", "cartao", "boleto">
    }
    Retorna a transação criada.
    """
    try:
        data = request.json or {}
        transacao = PagamentoService.criar_transacao(
            pedido_id, data.get("valor"), data.get("metodo_pagamento")
        )
        return jsonify(transacao), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


# Listar transações
@public_routes_pedidos.route("/pedidos/<pedido_id>/transacoes", methods=["GET"])
def listar_transacoes(pedido_id):
    # Lista todas as transações associadas a um pedido específico. Retorna id, valor, status e método de pagamento de cada transação.

    try:
        transacoes = PagamentoService.listar_transacoes(pedido_id)
        return jsonify(
            [
                {
                    "id": t.id,
                    "valor": float(t.valor),
                    "status": t.status.value,
                    "metodo_pagamento": t.metodo_pagamento,
                }
                for t in transacoes
            ]
        )
    except Exception as e:
        return jsonify({"erro": str(e)}), 400
