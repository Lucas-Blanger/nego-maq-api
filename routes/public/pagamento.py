from flask import Blueprint, request, jsonify
from services.public.PagamentosService import PagamentoService
from utils.middlewares.auth import token_required

pagamentos_routes = Blueprint("pagamentos", __name__)


# CRIAR PREFERÊNCIA DE PAGAMENTO (Checkout Mercado Pago)
@pagamentos_routes.route("/pedidos/<pedido_id>/pagamento/preferencia", methods=["POST"])
@token_required
def criar_preferencia(payload, pedido_id):
    try:
        resultado = PagamentoService.criar_preferencia_pagamento(pedido_id)
        return jsonify(resultado), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


# WEBHOOK MERCADO PAGO
@pagamentos_routes.route("/webhooks/mercadopago", methods=["POST"])
def webhook_mercadopago():

    # Recebe notificações do Mercado Pago sobre mudanças de status.

    try:
        data = request.json or request.form.to_dict()

        resultado = PagamentoService.processar_webhook_mercadopago(data)

        if resultado:
            return jsonify({"status": "processado", "resultado": resultado}), 200

        return jsonify({"status": "ignorado"}), 200

    except Exception as e:
        print(f"Erro ao processar webhook: {str(e)}")
        return jsonify({"erro": str(e)}), 400


# ESTORNAR PAGAMENTO
@pagamentos_routes.route("/transacoes/<transacao_id>/estornar", methods=["POST"])
@token_required
def estornar_pagamento(payload, transacao_id):
    """
    Estorna um pagamento (total ou parcial).

    Body (opcional): {
        "valor": 50.00  // Para estorno parcial
    }
    """
    try:
        data = request.json or {}
        valor = data.get("valor")

        resultado = PagamentoService.estornar_pagamento(transacao_id, valor)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


# CONSULTAR STATUS DE PAGAMENTO
@pagamentos_routes.route("/transacoes/<transacao_id>", methods=["GET"])
@token_required
def consultar_transacao(payload, transacao_id):
    # Consulta detalhes de uma transação
    try:
        from database.models import TransacaoPagamento

        transacao = TransacaoPagamento.query.get(transacao_id)
        if not transacao:
            return jsonify({"erro": "Transação não encontrada"}), 404

        return (
            jsonify(
                {
                    "transacao_id": transacao.id,
                    "pedido_id": transacao.pedido_id,
                    "valor": float(transacao.valor),
                    "status": transacao.status.value,
                    "metodo_pagamento": transacao.metodo_pagamento,
                    "mp_payment_id": transacao.mp_payment_id,
                    "criado_em": (
                        transacao.criado_em.isoformat() if transacao.criado_em else None
                    ),
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


# LISTAR TRANSAÇÕES DE UM PEDIDO
@pagamentos_routes.route("/pedidos/<pedido_id>/transacoes", methods=["GET"])
@token_required
def listar_transacoes(payload, pedido_id):
    # Lista todas as transações de um pedido
    try:
        transacoes = PagamentoService.listar_transacoes(pedido_id)
        return (
            jsonify(
                [
                    {
                        "transacao_id": t.id,
                        "valor": float(t.valor),
                        "status": t.status.value,
                        "metodo_pagamento": t.metodo_pagamento,
                        "mp_payment_id": t.mp_payment_id,
                        "criado_em": t.criado_em.isoformat() if t.criado_em else None,
                    }
                    for t in transacoes
                ]
            ),
            200,
        )
    except Exception as e:
        return jsonify({"erro": str(e)}), 400
