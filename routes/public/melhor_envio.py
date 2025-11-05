from flask import Blueprint, request, jsonify
import requests
from services.public.melhor_envio_service import (
    calcular_frete,
    rastrear_envio,
    obter_historico_rastreamento,
)
from utils.middlewares.auth import token_required
from database.models import Pedido
import os

frete_routes = Blueprint("frete", __name__, url_prefix="/frete")

MELHOR_ENVIO_API = os.getenv("MELHOR_ENVIO_API")
TOKEN = os.getenv("MELHOR_ENVIO_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Aplicacao (contato@negomaq.com.br)",
}


@frete_routes.route("/calcular-frete", methods=["POST"])
@token_required
def calcular(payload):

    # Calcula frete e retorna opções com TODOS os dados necessários. O front-end deve salvar o 'service_id' da opção escolhida!
    data = request.json

    try:
        resultado = calcular_frete(
            from_postal_code=data["from"],
            to_postal_code=data["to"],
            weight=data["weight"],
            height=data["height"],
            width=data["width"],
            length=data["length"],
        )
        opcoes = []
        for opcao in resultado:
            opcoes.append(
                {
                    "service_id": opcao.get("id"),
                    # Informações de exibição
                    "transportadora": opcao.get("company", {}).get("name"),
                    "servico": opcao.get("name"),
                    "servico_completo": f"{opcao.get('company', {}).get('name')} - {opcao.get('name')}",
                    # Valores
                    "preco": float(opcao.get("price", 0)),  # Converter para float
                    "preco_formatado": f"R$ {opcao.get('price', 0):.2f}",
                    # Prazos
                    "prazo_dias": opcao.get("delivery_time"),
                    "delivery_range": opcao.get("delivery_range", {}),
                    "prazo_minimo": opcao.get("delivery_range", {}).get("min"),
                    "prazo_maximo": opcao.get("delivery_range", {}).get("max"),
                }
            )

        return jsonify({"opcoes": opcoes, "total_opcoes": len(opcoes)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@frete_routes.route("/rastrear/<string:pedido_id>", methods=["GET"])
@token_required
def rastrear_pedido(payload, pedido_id):

    # Rastreia um pedido específico do usuário.

    try:
        usuario_id = payload["sub"]

        # Buscar pedido do usuário
        pedido = Pedido.query.filter_by(id=pedido_id, usuario_id=usuario_id).first()

        if not pedido:
            return jsonify({"error": "Pedido não encontrado"}), 404

        # Verificar se o pedido tem código de rastreamento
        melhor_envio_id = getattr(pedido, "melhor_envio_id", None)

        if not melhor_envio_id:
            return (
                jsonify(
                    {
                        "error": "Pedido ainda não possui rastreamento",
                        "status_pedido": pedido.status,
                        "mensagem": "O código de rastreamento será gerado após o pagamento e processamento do pedido.",
                    }
                ),
                400,
            )

        # Consultar rastreamento na API
        tracking_info = rastrear_envio(melhor_envio_id)

        # Mapear status para português
        status_map = {
            "pending": "Pendente",
            "paid": "Pago",
            "generated": "Etiqueta gerada",
            "posted": "Postado",
            "in_transit": "Em trânsito",
            "out_for_delivery": "Saiu para entrega",
            "delivered": "Entregue",
            "canceled": "Cancelado",
            "expired": "Expirado",
        }

        status_original = tracking_info.get("status", "")
        status_traduzido = status_map.get(status_original, status_original)

        return (
            jsonify(
                {
                    "pedido_id": pedido_id,
                    "melhor_envio_id": melhor_envio_id,
                    "codigo_rastreio": tracking_info.get("tracking"),
                    "codigo_rastreio_melhor_envio": tracking_info.get(
                        "melhorenvio_tracking"
                    ),
                    "status": status_original,
                    "status_descricao": status_traduzido,
                    "transportadora": pedido.frete_tipo,
                    "servico": pedido.frete_servico_nome,
                    "datas": {
                        "criado_em": tracking_info.get("created_at"),
                        "pago_em": tracking_info.get("paid_at"),
                        "etiqueta_gerada_em": tracking_info.get("generated_at"),
                        "postado_em": tracking_info.get("posted_at"),
                        "entregue_em": tracking_info.get("delivered_at"),
                        "cancelado_em": tracking_info.get("canceled_at"),
                    },
                    "valor_frete": (
                        float(pedido.frete_valor) if pedido.frete_valor else 0
                    ),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Erro ao rastrear pedido: {str(e)}"}), 500


@frete_routes.route("/rastrear/codigo/<tracking_code>", methods=["GET"])
@token_required
def rastrear_por_codigo(payload, tracking_code):
    # Rastreia um envio pelo código de rastreamento.
    try:
        tracking_info = obter_historico_rastreamento(tracking_code)

        return (
            jsonify({"codigo_rastreio": tracking_code, "informacoes": tracking_info}),
            200,
        )

    except Exception as e:
        return jsonify({"error": f"Erro ao consultar rastreamento: {str(e)}"}), 500


@frete_routes.route("/meus-rastreamentos", methods=["GET"])
@token_required
def listar_rastreamentos(payload):
    try:
        usuario_id = payload["sub"]

        # Buscar pedidos do usuário que têm código de rastreamento
        pedidos = (
            Pedido.query.filter(
                Pedido.usuario_id == usuario_id, Pedido.melhor_envio_id.isnot(None)
            )
            .order_by(Pedido.criado_em.desc())
            .all()
        )

        if not pedidos:
            return (
                jsonify(
                    {
                        "mensagem": "Você ainda não possui pedidos com rastreamento",
                        "pedidos": [],
                    }
                ),
                200,
            )

        order_ids = [p.melhor_envio_id for p in pedidos]

        url = f"{MELHOR_ENVIO_API}/me/shipment/tracking"
        response = requests.post(
            url,
            headers=HEADERS,
            json={"orders": order_ids},
            timeout=20,
        )
        response.raise_for_status()
        tracking_data = response.json()

        # Montar resultado
        resultado = []
        for pedido in pedidos:
            tracking_info = tracking_data.get(pedido.melhor_envio_id, {})

            resultado.append(
                {
                    "pedido_id": pedido.id,
                    "codigo_rastreio": tracking_info.get("tracking"),
                    "status": tracking_info.get("status"),
                    "transportadora": pedido.frete_tipo,
                    "data_pedido": (
                        pedido.criado_em.isoformat() if pedido.criado_em else None
                    ),
                    "valor_total": (
                        float(pedido.valor_total) if pedido.valor_total else 0
                    ),
                }
            )

        return jsonify({"total": len(resultado), "pedidos": resultado}), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao listar rastreamentos: {str(e)}"}), 500
