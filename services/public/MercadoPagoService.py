import os
import mercadopago

MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")
BASE_URL = os.environ.get("BASE_URL")


class MercadoPagoService:

    def __init__(self):
        if not MERCADOPAGO_ACCESS_TOKEN:
            raise ValueError("MERCADOPAGO_ACCESS_TOKEN não configurado")
        self.sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)

    def criar_preferencia_pagamento(self, pedido, itens):
        """
        Cria uma preferência de pagamento.
        O cliente será redirecionado para o Mercado Pago onde poderá escolher:
        - Cartão de crédito/débito
        - PIX
        - Boleto bancário

        Returns:
            {
                "preference_id": "xxx",
                "init_point": "https://mercadopago.com/...",
                "sandbox_init_point": "https://sandbox.mercadopago.com/..."
            }
        """
        # Preparar itens
        mp_items = []
        for item in itens:
            mp_items.append(
                {
                    "id": item["produto_id"],
                    "title": item["nome"],
                    "description": item.get("descricao", "")[:256],
                    "picture_url": item.get("img"),
                    "category_id": item.get("categoria", "others"),
                    "quantity": item["quantidade"],
                    "unit_price": float(item["preco_unitario"]),
                    "currency_id": "BRL",
                }
            )

        # Adicionar frete como item separado
        if pedido.frete_valor and pedido.frete_valor > 0:
            # Montar nome descritivo do frete
            nome_frete = "Frete"

            if hasattr(pedido, "frete_servico_nome") and pedido.frete_servico_nome:
                nome_frete = f"Frete - {pedido.frete_servico_nome}"
            elif pedido.frete_tipo:
                nome_frete = f"Frete - {pedido.frete_tipo}"

            mp_items.append(
                {
                    "title": nome_frete,
                    "description": "Entrega para o endereço cadastrado",
                    "quantity": 1,
                    "unit_price": float(pedido.frete_valor),
                    "currency_id": "BRL",
                }
            )

        # Configuração da preferência
        preference_data = {
            "items": mp_items,
            "payer": {
                "name": getattr(pedido.usuario, "nome", ""),
                "email": getattr(pedido.usuario, "email", ""),
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
                "success": f"{BASE_URL}/pagamento/sucesso",
                "failure": f"{BASE_URL}/pagamento/falha",
                "pending": f"{BASE_URL}/pagamento/pendente",
            },
            "auto_return": "approved",
            "external_reference": str(pedido.id),
            "notification_url": f"{API_BASE_URL}/webhooks/mercadopago",
            "statement_descriptor": "NEGO-MAQ",
            "payment_methods": {
                "installments": 12,  # Máximo de parcelas
                "default_installments": 1,
            },
        }

        # Criar preferência no Mercado Pago
        preference_response = self.sdk.preference().create(preference_data)

        if preference_response.get("status") not in [200, 201]:
            raise ValueError(f"Erro ao criar preferência: {preference_response}")

        preference = preference_response["response"]

        if "id" not in preference or "init_point" not in preference:
            raise ValueError(f"Preferência inválida: {preference}")

        return {
            "preference_id": preference["id"],
            "init_point": preference["init_point"],
            "sandbox_init_point": preference.get("sandbox_init_point"),
        }

    def consultar_pagamento(self, payment_id):
        # Consulta detalhes de um pagamento específico
        payment_response = self.sdk.payment().get(payment_id)

        if payment_response.get("status") != 200:
            raise ValueError(f"Pagamento {payment_id} não encontrado")

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

        # Processa notificações de webhook do Mercado Pago.
        try:
            topic = data.get("topic") or data.get("type")
            print(f"[MercadoPago] Webhook tipo: {topic}")

            if topic == "merchant_order":
                return self._processar_merchant_order(data)
            elif topic == "payment":
                return self._processar_payment(data)
            else:
                raise ValueError(f"Tipo de webhook não suportado: {topic}")

        except Exception as e:
            print(f"Erro ao processar webhook: {e}")
            raise

    def _processar_merchant_order(self, data):
        # Processa webhook de merchant_order
        resource = data.get("resource", "")
        order_id = (
            resource.rstrip("/").split("/")[-1] if "http" in str(resource) else resource
        )

        if not order_id:
            raise ValueError(f"ID da ordem não encontrado: {data}")

        print(f"[MercadoPago] Buscando merchant_order: {order_id}")

        ordem = self.sdk.merchant_order().get(order_id)

        if not ordem or ordem.get("status") != 200:
            raise ValueError(f"Ordem {order_id} não encontrada")

        body = ordem["response"]
        payments = body.get("payments", [])

        if not payments:
            print(f"[MercadoPago] Ordem ainda sem pagamentos")
            return {
                "type": "merchant_order",
                "payment_id": None,
                "status": "pending",
                "pedido_id": body.get("external_reference"),
            }

        primeiro_pagamento = payments[0]
        print(
            f"[MercadoPago] Pagamento: {primeiro_pagamento.get('id')} - {primeiro_pagamento.get('status')}"
        )

        return {
            "type": "merchant_order",
            "payment_id": (
                str(primeiro_pagamento.get("id"))
                if primeiro_pagamento.get("id")
                else None
            ),
            "status": primeiro_pagamento.get("status"),
            "pedido_id": body.get("external_reference"),
        }

    def _processar_payment(self, data):
        # Processa webhook de payment
        payment_id = (
            data.get("data", {}).get("id") or data.get("resource") or data.get("id")
        )

        if isinstance(payment_id, str) and "http" in payment_id:
            payment_id = payment_id.rstrip("/").split("/")[-1]

        if not payment_id:
            raise ValueError(f"ID do pagamento não encontrado: {data}")

        print(f"[MercadoPago] Buscando pagamento: {payment_id}")

        pagamento = self.sdk.payment().get(payment_id)

        if not pagamento or pagamento.get("status") != 200:
            raise ValueError(f"Pagamento {payment_id} não encontrado")

        body = pagamento["response"]
        print(f"[MercadoPago] Status: {body.get('status')}")

        return {
            "type": "payment",
            "payment_id": str(payment_id),
            "status": body.get("status"),
            "pedido_id": body.get("external_reference"),
        }

    def estornar_pagamento(self, payment_id, valor=None):
        # Estorna um pagamento (total ou parcial). Se valor não informado, estorna o valor total.

        refund_data = {}
        if valor:
            refund_data["amount"] = float(valor)

        refund_response = self.sdk.refund().create(payment_id, refund_data)

        if refund_response.get("status") not in [200, 201]:
            raise ValueError(f"Erro ao estornar: {refund_response}")

        refund = refund_response["response"]

        return {
            "refund_id": refund["id"],
            "payment_id": refund["payment_id"],
            "amount": refund["amount"],
            "status": refund["status"],
        }
