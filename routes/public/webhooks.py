from flask import Blueprint, request, jsonify
from services.pagamento_service import MercadoPagoService
from services.pagamentos_service import PagamentoService
from database.models import Pedido, StatusPedidoEnum
from database import db
import logging
import json

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/api/public/webhooks')

@webhooks_bp.route('/mercadopago', methods=['POST'])
def webhook_mercadopago():
    """Webhook para notificações do Mercado Pago"""
    try:
        # Log do webhook recebido
        raw_data = request.get_data()
        headers = dict(request.headers)
        
        logging.info(f"Webhook MP recebido - Headers: {headers}")
        logging.info(f"Webhook MP recebido - Body: {raw_data.decode('utf-8') if raw_data else 'Empty'}")
        
        # Tentar obter JSON
        try:
            data = request.get_json()
        except Exception as e:
            logging.error(f"Erro ao parsear JSON do webhook: {str(e)}")
            return jsonify({"status": "error", "message": "JSON inválido"}), 400
        
        if not data:
            logging.warning("Webhook MP recebido sem dados JSON")
            return jsonify({"status": "ok", "message": "Sem dados para processar"}), 200
        
        # Processar notificação
        notification_type = data.get('type')
        action = data.get('action')
        
        logging.info(f"Webhook MP - Type: {notification_type}, Action: {action}")
        
        # Verificar se é notificação de pagamento
        if notification_type == 'payment':
            payment_id = data.get('data', {}).get('id')
            
            if not payment_id:
                logging.error("Payment ID não encontrado no webhook")
                return jsonify({"status": "error", "message": "Payment ID ausente"}), 400
            
            # Verificar o pagamento no MP
            try:
                mp_service = MercadoPagoService()
                payment_info = mp_service.verificar_pagamento(payment_id)
            except Exception as e:
                logging.error(f"Erro ao instanciar MercadoPagoService: {str(e)}")
                return jsonify({"status": "error", "message": "Erro de configuração"}), 500
            
            if not payment_info:
                logging.error(f"Não foi possível obter informações do pagamento {payment_id}")
                return jsonify({"status": "error", "message": "Pagamento não encontrado"}), 404
            
            # Extrair dados do pagamento
            pedido_id = payment_info.get('external_reference')
            status = payment_info.get('status')
            transaction_amount = payment_info.get('transaction_amount')
            payment_method_id = payment_info.get('payment_method_id')
            
            logging.info(f"Processando pagamento {payment_id} - Pedido: {pedido_id}, Status: {status}")
            
            if not pedido_id:
                logging.error("External reference (pedido_id) não encontrado")
                return jsonify({"status": "error", "message": "Pedido não identificado"}), 400
            
            # Buscar pedido no banco
            try:
                pedido = Pedido.query.get(pedido_id)
                if not pedido:
                    logging.error(f"Pedido {pedido_id} não encontrado no banco")
                    return jsonify({"status": "error", "message": "Pedido não encontrado"}), 404
            except Exception as e:
                logging.error(f"Erro ao buscar pedido {pedido_id}: {str(e)}")
                return jsonify({"status": "error", "message": "Erro no banco de dados"}), 500
            
            # Processar baseado no status do pagamento
            try:
                if status == 'approved':
                    # Pagamento aprovado
                    pedido.status = StatusPedidoEnum.PAGO
                    
                    # Criar transação se não existir
                    try:
                        PagamentoService.criar_transacao(
                            pedido_id=pedido.id,
                            valor=transaction_amount,
                            metodo_pagamento=payment_method_id or 'mercado_pago'
                        )
                        logging.info(f"Transação criada para pedido {pedido_id}")
                    except Exception as e:
                        logging.error(f"Erro ao criar transação: {str(e)}")
                        # Continua mesmo com erro na transação
                    
                    logging.info(f"✅ Pagamento APROVADO para pedido {pedido_id}")
                    
                elif status == 'rejected':
                    pedido.status = StatusPedidoEnum.CANCELADO
                    logging.info(f"❌ Pagamento REJEITADO para pedido {pedido_id}")
                    
                elif status == 'pending':
                    pedido.status = StatusPedidoEnum.PENDENTE
                    logging.info(f"⏳ Pagamento PENDENTE para pedido {pedido_id}")
                    
                elif status == 'cancelled':
                    pedido.status = StatusPedidoEnum.CANCELADO
                    logging.info(f"🚫 Pagamento CANCELADO para pedido {pedido_id}")
                    
                else:
                    logging.warning(f"Status não tratado: {status} para pedido {pedido_id}")
                
                # Salvar no banco
                db.session.commit()
                logging.info(f"Status do pedido {pedido_id} atualizado para: {pedido.status.name}")
                
            except Exception as e:
                db.session.rollback()
                logging.error(f"Erro ao atualizar pedido {pedido_id}: {str(e)}")
                return jsonify({"status": "error", "message": "Erro ao atualizar pedido"}), 500
        
        else:
            logging.info(f"Webhook ignorado - Type: {notification_type}")
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logging.error(f"Erro geral no webhook MP: {str(e)}")
        return jsonify({"status": "error", "message": "Erro interno"}), 500

@webhooks_bp.route('/test', methods=['GET', 'POST'])
def test_webhook():
    """Endpoint de teste para webhooks"""
    try:
        method = request.method
        data = None
        
        if method == 'POST':
            data = request.get_json()
        
        logging.info(f"Webhook de teste acessado - Método: {method}")
        
        return jsonify({
            "status": "ok",
            "message": "Webhook funcionando",
            "method": method,
            "data": data,
            "headers": dict(request.headers)
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500