from flask import Blueprint, request, jsonify
from services.public.pedidos_service import PedidoService
from services.public.pagamentos_service import PagamentoService
from services.public.melhor_envio_service import calcular_frete_pedido
from utils.middlewares.auth import token_required
import os

public_routes_pedidos = Blueprint("pedidos_public", __name__)


EMPRESA_CEP = os.getenv("EMPRESA_CEP")


# CRIAR UM NOVO PEDIDO
@public_routes_pedidos.route("/pedidos", methods=["POST"])
@token_required
def criar_pedido(payload):
    try:
        data = request.json
        pedido = PedidoService.criar_pedido(data)
        return jsonify(pedido), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


# RESUMO DO FRETE
@public_routes_pedidos.route("/pedidos/<pedido_id>/frete/resumo", methods=["GET"])
@token_required
def resumo_frete(payload, pedido_id):
    pedido = PedidoService.obter_pedido(pedido_id)
    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    if not pedido.endereco:
        return jsonify({"erro": "Endereço do pedido não encontrado"}), 400

    itens = [
        {
            "produto_id": i.produto_id,
            "quantidade": i.quantidade,
            "peso": float(i.peso) if i.peso else 0,
            "comprimento": float(i.comprimento) if i.comprimento else 0,
            "altura": float(i.altura) if i.altura else 0,
            "largura": float(i.largura) if i.largura else 0,
        }
        for i in pedido.itens
    ]

    peso_total = sum(i["peso"] * i["quantidade"] for i in itens)

    return jsonify(
        {
            "pedido_id": pedido.id,
            "cep_origem": EMPRESA_CEP,
            "cep_destino": pedido.endereco.cep,
            "itens": itens,
            "peso_total": peso_total,
        }
    )


# COTAÇÃO DE FRETE
@public_routes_pedidos.route("/pedidos/<pedido_id>/frete/cotacao", methods=["POST"])
@token_required
def cotacao_frete(payload, pedido_id):
    try:
        data = request.json
        cep_destino = data.get("cep_destino")

        if not cep_destino:
            return jsonify({"erro": "cep_destino é obrigatório"}), 400

        pedido = PedidoService.obter_pedido(pedido_id)
        if not pedido:
            return jsonify({"erro": "Pedido não encontrado"}), 404

        if not pedido.endereco:
            return jsonify({"erro": "Endereço do pedido não encontrado"}), 400

        # Preparar itens para cálculo
        itens = [
            {
                "peso": float(i.peso) if i.peso else 0,
                "comprimento": float(i.comprimento) if i.comprimento else 0,
                "altura": float(i.altura) if i.altura else 0,
                "largura": float(i.largura) if i.largura else 0,
                "quantidade": i.quantidade,
            }
            for i in pedido.itens
        ]

        # Calcular frete usando a API do Melhor Envio
        opcoes_frete = calcular_frete_pedido(
            cep_origem=pedido.endereco.cep, cep_destino=cep_destino, itens=itens
        )

        # Formatar resposta
        resultado = {
            "pedido_id": pedido.id,
            "cep_origem": EMPRESA_CEP,
            "cep_destino": cep_destino,
            "opcoes": [],
        }

        # Processar e FILTRAR cada opção de frete
        for opcao in opcoes_frete:
            preco = float(opcao.get("price", 0))
            prazo_dias = opcao.get("delivery_time")

            # FILTRAR: apenas opções com preço válido e prazo definido
            if preco > 0 and prazo_dias is not None:
                resultado["opcoes"].append(
                    {
                        "id": opcao.get("id"),
                        "transportadora": opcao.get("company", {}).get("name"),
                        "servico": opcao.get("name"),
                        "preco": preco,
                        "prazo_dias": prazo_dias,
                        "prazo_min": opcao.get("delivery_range", {}).get("min"),
                        "prazo_max": opcao.get("delivery_range", {}).get("max"),
                        "disponivel": True,
                    }
                )

        # Ordenar por preço (do mais barato ao mais caro)
        resultado["opcoes"].sort(key=lambda x: x["preco"])

        if resultado["opcoes"]:
            resultado["opcao_mais_barata"] = resultado["opcoes"][0]
            resultado["opcao_mais_rapida"] = min(
                resultado["opcoes"], key=lambda x: x["prazo_dias"]
            )

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 400


# OBTER PEDIDO
@public_routes_pedidos.route("/pedidos/<pedido_id>", methods=["GET"])
@token_required
def obter_pedido(pedido_id):
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


# PEDIDOS POR USUÁRIO
@public_routes_pedidos.route("/usuarios/<usuario_id>/pedidos", methods=["GET"])
@token_required
def pedidos_usuario(usuario_id):
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


# CRIAR TRANSAÇÃO
@public_routes_pedidos.route("/pedidos/<pedido_id>/transacoes", methods=["POST"])
@token_required
def criar_transacao(pedido_id):
    try:
        data = request.json or {}
        transacao = PagamentoService.criar_transacao(
            pedido_id, data.get("valor"), data.get("metodo_pagamento")
        )
        return jsonify(transacao), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


# LISTAR TRANSAÇÕES
@public_routes_pedidos.route("/pedidos/<pedido_id>/transacoes", methods=["GET"])
@token_required
def listar_transacoes(pedido_id):
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
