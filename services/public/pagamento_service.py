import mercadopago
import os
from flask import current_app
import logging

class MercadoPagoService:
    def __init__(self):
        self.token = os.getenv("MERCADO_PAGO_TOKEN")
        if not self.token:
            raise ValueError("Token do Mercado Pago não configurado")
        
        self.sdk = mercadopago.SDK(self.token)
        self.webhook_secret = os.getenv("MERCADO_PAGO_WEBHOOK_SECRET")
    
    def criar_preferencia(self, pedido_data):
        """Cria uma preferência de pagamento no Mercado Pago"""
        try:
            # Preparar itens do pedido
            items = []
            valor_total = 0
            
            for item in pedido_data.get('itens', []):
                preco_unitario = float(item['preco_unitario'])
                quantidade = int(item['quantidade'])
                subtotal = preco_unitario * quantidade
                valor_total += subtotal
                
                items.append({
                    "id": str(item['produto_id']),
                    "title": item['nome'][:126],  # MP limita a 256 chars
                    "description": item.get('descricao', '')[:254],
                    "quantity": quantidade,
                    "currency_id": "BRL",
                    "unit_price": preco_unitario
                })
            
            # Adicionar frete se houver
            if pedido_data.get('frete_valor', 0) > 0:
                frete_valor = float(pedido_data['frete_valor'])
                valor_total += frete_valor
                
                items.append({
                    "id": "frete",
                    "title": f"Frete - {pedido_data.get('frete_tipo', 'Padrão')}",
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": frete_valor
                })
            
            # URLs de retorno
            frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:9000')
            api_url = current_app.config.get('API_BASE_URL', 'http://localhost:5000')
            
            preference_data = {
                "items": items,
                "payer": {
                    "email": pedido_data['cliente_email'],
                    "name": pedido_data.get('cliente_nome', ''),
                    "surname": pedido_data.get('cliente_sobrenome', ''),
                },
                "back_urls": {
                    "success": f"{frontend_url}/pagamento/sucesso",
                    "failure": f"{frontend_url}/pagamento/erro", 
                    "pending": f"{frontend_url}/pagamento/pendente"
                },
                "notification_url": f"{api_url}/api/public/webhooks/mercadopago",
                "external_reference": str(pedido_data['pedido_id']),
                "auto_return": "approved",
                "payment_methods": {
                    "installments": 12,
                    "default_installments": 1
                },
                "statement_descriptor": "NEGO MAQ",
                "expires": True,
                "expiration_date_from": None,
                "expiration_date_to": None
            }
            
            # Adicionar endereço se disponível
            if pedido_data.get('cep'):
                preference_data["shipments"] = {
                    "receiver_address": {
                        "zip_code": pedido_data.get('cep', '').replace('-', ''),
                        "state_name": pedido_data.get('estado', ''),
                        "city_name": pedido_data.get('cidade', ''),
                        "street_name": pedido_data.get('logradouro', ''),
                        "street_number": pedido_data.get('numero', '')
                    }
                }
            
            logging.info(f"Criando preferência MP para pedido {pedido_data['pedido_id']}")
            
            response = self.sdk.preference().create(preference_data)
            
            if response["status"] == 201:
                preference = response["response"]
                return {
                    "success": True,
                    "preference_id": preference["id"],
                    "init_point": preference["init_point"],
                    "sandbox_init_point": preference.get("sandbox_init_point")
                }
            else:
                logging.error(f"Erro MP: {response}")
                return {"success": False, "error": "Erro ao criar preferência"}
                
        except Exception as e:
            logging.error(f"Erro ao criar preferência MP: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def verificar_pagamento(self, payment_id):
        """Verifica o status de um pagamento"""
        try:
            payment_response = self.sdk.payment().get(payment_id)
            if payment_response["status"] == 200:
                return payment_response["response"]
            return None
        except Exception as e:
            logging.error(f"Erro ao verificar pagamento: {str(e)}")
            return None

# Função legacy para compatibilidade
def criar_pagamento(preco, descricao, email_cliente, id_pedido):
    """Função legacy - usar MercadoPagoService.criar_preferencia() ao invés"""
    try:
        service = MercadoPagoService()
        pedido_data = {
            'pedido_id': id_pedido,
            'cliente_email': email_cliente,
            'itens': [{
                'produto_id': 'legacy',
                'nome': descricao,
                'descricao': descricao,
                'quantidade': 1,
                'preco_unitario': preco
            }]
        }
        
        resultado = service.criar_preferencia(pedido_data)
        if resultado["success"]:
            return resultado["init_point"]
        else:
            raise Exception(resultado["error"])
            
    except Exception as e:
        logging.error(f"Erro função legacy: {str(e)}")
        raise e