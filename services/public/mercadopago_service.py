import os
import mercadopago
from decimal import Decimal

MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
MERCADOPAGO_PUBLIC_KEY = os.getenv("MERCADO_PAGO_PUBLIC_KEY")

API_BASE_URL = os.getenv("API_BASE_URL", "https://seudominio.com")


class MercadoPagoService:

    def __init__(self):
        self.sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)

    def criar_preferencia_pagamento(self, pedido, itens):
        """
        Cria uma preferência de pagamento no Mercado Pago.
        Retorna o link para checkout e o preference_id.

        Args:
            pedido: objeto Pedido
            itens: lista de itens do pedido com produto info

        Returns:
            {
                "preference_id": "xxx",
                "init_point": "https://mercadopago.com/...",
                "sandbox_init_point": "https://sandbox.mercadopago.com/..."
            }
        """

        # Preparar itens para o Mercado Pago
        mp_items = []
        for item in itens:
            mp_items.append(
                {
                    "id": item["produto_id"],
                    "title": item["nome"],
                    "description": item.get("descricao", "")[:256],  # max 256 chars
                    "picture_url": item.get("img"),
                    "category_id": item.get("categoria", "others"),
                    "quantity": item["quantidade"],
                    "unit_price": float(item["preco_unitario"]),
                    "currency_id": "BRL",
                }
            )

        # Adicionar frete como item separado
        if pedido.frete_valor and pedido.frete_valor > 0:
            mp_items.append(
                {
                    "title": f"Frete - {pedido.frete_tipo or 'Entrega'}",
                    "quantity": 1,
                    "unit_price": float(pedido.frete_valor),
                    "currency_id": "BRL",
                }
            )

        # Dados da preferência
        preference_data = {
            "items": mp_items,
            "payer": {
                "name": pedido.usuario.nome if hasattr(pedido.usuario, "nome") else "",
                "email": (
                    pedido.usuario.email if hasattr(pedido.usuario, "email") else ""
                ),
                "phone": {"number": getattr(pedido.usuario, "telefone", "")},
                "address": {
                    "zip_code": pedido.endereco.cep if pedido.endereco else "",
                    "street_name": (
                        pedido.endereco.logradouro if pedido.endereco else ""
                    ),
                    "street_number": pedido.endereco.numero if pedido.endereco else "",
                },
            },
            "back_urls": {
                "success": f"{API_BASE_URL}/pagamento/sucesso",
                "failure": f"{API_BASE_URL}/pagamento/falha",
                "pending": f"{API_BASE_URL}/pagamento/pendente",
            },
            "auto_return": "approved",
            "external_reference": pedido.id,  # ID do seu pedido
            "notification_url": f"{API_BASE_URL}/webhooks/mercadopago",
            "statement_descriptor": "SUA LOJA",
            "payment_methods": {
                "excluded_payment_methods": [],
                "excluded_payment_types": [],
                "installments": 12,  # Parcelas máximas
                "default_installments": 1,
            },
            "shipments": {
                "cost": float(pedido.frete_valor) if pedido.frete_valor else 0,
                "mode": "not_specified",
            },
        }

        # Criar preferência
        preference_response = self.sdk.preference().create(preference_data)
        preference = preference_response["response"]

        if "id" not in preference or "init_point" not in preference:
            raise ValueError(f"Erro ao criar preferência: {preference}")

        return {
            "preference_id": preference["id"],
            "init_point": preference["init_point"],
            "sandbox_init_point": preference.get("sandbox_init_point"),
        }

    def processar_pagamento_pix(self, pedido, email_pagador):
        """
        Cria um pagamento PIX.
        Retorna QR Code e código copia e cola.
        """
        payment_data = {
            "transaction_amount": float(pedido.valor_total),
            "description": f"Pedido #{pedido.id}",
            "payment_method_id": "pix",
            "payer": {"email": email_pagador},
            "external_reference": pedido.id,
            "notification_url": f"{API_BASE_URL}/webhooks/mercadopago",
        }

        payment_response = self.sdk.payment().create(payment_data)
        payment = payment_response["response"]

        return {
            "payment_id": payment["id"],
            "status": payment["status"],
            "qr_code": payment["point_of_interaction"]["transaction_data"]["qr_code"],
            "qr_code_base64": payment["point_of_interaction"]["transaction_data"][
                "qr_code_base64"
            ],
            "ticket_url": payment["point_of_interaction"]["transaction_data"][
                "ticket_url"
            ],
        }

    def processar_pagamento_cartao(
        self, pedido, token_cartao, email_pagador, installments=1, issuer_id=None
    ):
        """
        Processa pagamento com cartão de crédito.

        Args:
            token_cartao: Token do cartão gerado no front-end
            installments: Número de parcelas
            issuer_id: ID do banco emissor
        """
        payment_data = {
            "transaction_amount": float(pedido.valor_total),
            "token": token_cartao,
            "description": f"Pedido #{pedido.id}",
            "installments": installments,
            "payment_method_id": "visa",  # ou detectar automaticamente
            "payer": {"email": email_pagador},
            "external_reference": pedido.id,
            "notification_url": f"{API_BASE_URL}/webhooks/mercadopago",
        }

        if issuer_id:
            payment_data["issuer_id"] = issuer_id

        payment_response = self.sdk.payment().create(payment_data)
        payment = payment_response["response"]

        return {
            "payment_id": payment["id"],
            "status": payment["status"],
            "status_detail": payment["status_detail"],
            "installments": payment.get("installments"),
            "transaction_amount": payment["transaction_amount"],
        }

    def consultar_pagamento(self, payment_id):
        """Consulta status de um pagamento"""
        payment_response = self.sdk.payment().get(payment_id)
        payment = payment_response["response"]

        return {
            "id": payment["id"],
            "status": payment["status"],
            "status_detail": payment["status_detail"],
            "external_reference": payment.get("external_reference"),
            "transaction_amount": payment["transaction_amount"],
            "date_approved": payment.get("date_approved"),
            "payment_method_id": payment["payment_method_id"],
        }

    def processar_webhook(self, data):
        """
        Processa notificações do webhook do Mercado Pago.

        Status possíveis:
        - pending: Pagamento pendente
        - approved: Pagamento aprovado
        - authorized: Pagamento autorizado
        - in_process: Em processamento
        - in_mediation: Em disputa
        - rejected: Rejeitado
        - cancelled: Cancelado
        - refunded: Estornado
        - charged_back: Chargeback
        """

        # Mercado Pago envia topic e id
        topic = data.get("topic") or data.get("type")
        resource_id = data.get("id") or data.get("data", {}).get("id")

        if topic == "payment":
            payment_info = self.consultar_pagamento(resource_id)
            return {
                "type": "payment",
                "payment_id": payment_info["id"],
                "status": payment_info["status"],
                "pedido_id": payment_info.get("external_reference"),
                "valor": payment_info["transaction_amount"],
            }

        return None

    def estornar_pagamento(self, payment_id, valor=None):
        """
        Estorna um pagamento (total ou parcial).
        Se valor não for informado, estorna o valor total.
        """
        refund_data = {}
        if valor:
            refund_data["amount"] = float(valor)

        refund_response = self.sdk.refund().create(payment_id, refund_data)
        refund = refund_response["response"]

        return {
            "refund_id": refund["id"],
            "payment_id": refund["payment_id"],
            "amount": refund["amount"],
            "status": refund["status"],
        }
