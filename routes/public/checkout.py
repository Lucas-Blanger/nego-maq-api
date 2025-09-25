from flask import Blueprint, request, jsonify
from services.public.melhor_envio import MelhorEnvioService
from services.public.pagamento_service import MercadoPagoService
from services.public.pedidos_service import PedidoService
from database.models import Usuario, Endereco, Produto
from utils.auth import token_required
import logging

checkout_bp = Blueprint('checkout', __name__, url_prefix='/api/checkout')

@checkout_bp.route('/calcular-frete', methods=['POST'])
def calcular_frete():
    """Calcula o frete para o carrinho"""
    try:
        data = request.get_json()
        destino_cep = data.get('cep')
        produtos = data.get('produtos', [])
        
        if not destino_cep or not produtos:
            return jsonify({"erro": "CEP e produtos são obrigatórios"}), 400
        
        # CEP de origem (sua empresa)
        origem_cep = "99700-000"  # Substitua pelo seu CEP
        
        melhor_envio = MelhorEnvioService()
        resultado = melhor_envio.calcular_frete(origem_cep, destino_cep, produtos)
        
        if resultado["success"]:
            return jsonify(resultado["servicos"]), 200
        else:
            return jsonify({"erro": resultado["error"]}), 400
            
    except Exception as e:
        logging.error(f"Erro ao calcular frete: {str(e)}")
        return jsonify({"erro": "Erro interno do servidor"}), 500

@checkout_bp.route('/criar-pedido', methods=['POST'])
@token_required
def criar_pedido_completo(payload):
    """Cria pedido com pagamento e frete"""
    try:
        data = request.get_json()
        
        # 1. Criar pedido
        pedido_data = {
            "usuario_id": payload["id"],
            "itens": data.get("itens", [])
        }
        
        resultado_pedido = PedidoService.criar_pedido(pedido_data)
        pedido_id = resultado_pedido["pedido_id"]
        
        # 2. Buscar dados do usuário e endereço
        usuario = Usuario.query.get(payload["id"])
        endereco = Endereco.query.filter_by(usuario_id=payload["id"]).first()
        
        if not endereco:
            return jsonify({"erro": "Usuário não possui endereço cadastrado"}), 400
        
        # 3. Preparar dados para o Mercado Pago
        mp_data = {
            "pedido_id": pedido_id,
            "cliente_email": usuario.email,
            "cliente_nome": usuario.nome,
            "cliente_sobrenome": usuario.sobrenome,
            "cliente_telefone": usuario.telefone,
            "cep": endereco.cep,
            "cidade": endereco.cidade,
            "estado": endereco.estado,
            "logradouro": endereco.logradouro,
            "numero": endereco.numero,
            "itens": []
        }
        
        # Adicionar itens ao MP
        for item in data.get("itens", []):
            produto = Produto.query.get(item["produto_id"])
            if produto:
                mp_data["itens"].append({
                    "produto_id": produto.id,
                    "nome": produto.nome,
                    "descricao": produto.descricao,
                    "quantidade": item.get("quantidade", 1),
                    "preco_unitario": produto.preco
                })
        
        # Adicionar frete se fornecido
        if data.get("frete_valor") and data.get("frete_tipo"):
            mp_data["frete_valor"] = data["frete_valor"]
            mp_data["frete_tipo"] = data["frete_tipo"]
        
        # 4. Criar preferência no Mercado Pago
        mp_service = MercadoPagoService()
        resultado_mp = mp_service.criar_preferencia(mp_data)
        
        if not resultado_mp["success"]:
            return jsonify({"erro": "Erro ao criar pagamento"}), 400
        
        return jsonify({
            "pedido_id": pedido_id,
            "valor_total": resultado_pedido["valor_total"],
            "pagamento": {
                "preference_id": resultado_mp["preference_id"],
                "init_point": resultado_mp["init_point"],
                "sandbox_init_point": resultado_mp.get("sandbox_init_point")
            }
        }), 201
        
    except Exception as e:
        logging.error(f"Erro ao criar pedido completo: {str(e)}")
        return jsonify({"erro": "Erro interno do servidor"}), 500