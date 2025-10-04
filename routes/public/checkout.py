from flask import Blueprint, request, jsonify
from services.public.melhor_envio import MelhorEnvioService
from services.public.pagamento_service import MercadoPagoService
from services.public.pedidos_service import PedidoService
from database.models import Usuario, Endereco, Produto
from utils.auth import token_required
import logging
import os

checkout_bp = Blueprint('checkout', __name__, url_prefix='/api/public/checkout')

@checkout_bp.route('/calcular-frete', methods=['POST'])
def calcular_frete():
    """Calcula o frete para o carrinho"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"erro": "Dados não fornecidos"}), 400
            
        destino_cep = data.get('cep')
        produtos = data.get('produtos', [])
        
        if not destino_cep:
            return jsonify({"erro": "CEP de destino é obrigatório"}), 400
            
        if not produtos:
            return jsonify({"erro": "Lista de produtos é obrigatória"}), 400
        
        # CEP de origem (sua empresa - Erechim/RS)
        origem_cep = os.getenv("EMPRESA_CEP", "99713253")
        
        # Instanciar serviço
        melhor_envio = MelhorEnvioService()
        
        # Calcular frete
        resultado = melhor_envio.calcular_frete(origem_cep, destino_cep, produtos)
        
        if resultado["success"]:
            return jsonify({
                "success": True,
                "servicos": resultado["servicos"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "erro": resultado["error"]
            }), 400
            
    except Exception as e:
        logging.error(f"Erro ao calcular frete: {str(e)}")
        return jsonify({
            "success": False,
            "erro": "Erro interno do servidor"
        }), 500

@checkout_bp.route('/criar-pedido', methods=['POST'])
@token_required
def criar_pedido_completo(payload):
    """Cria pedido com pagamento"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"erro": "Dados não fornecidos"}), 400
        
        # 1. Validar dados básicos
        itens = data.get("itens", [])
        if not itens:
            return jsonify({"erro": "Itens do pedido são obrigatórios"}), 400
        
        # 2. Criar pedido
        pedido_data = {
            "usuario_id": payload["id"],
            "itens": itens
        }
        
        resultado_pedido = PedidoService.criar_pedido(pedido_data)
        pedido_id = resultado_pedido["pedido_id"]
        
        logging.info(f"Pedido {pedido_id} criado para usuário {payload['id']}")
        
        # 3. Buscar dados do usuário e endereço
        usuario = Usuario.query.get(payload["id"])
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404
            
        endereco = Endereco.query.filter_by(usuario_id=payload["id"]).first()
        if not endereco:
            return jsonify({"erro": "Usuário não possui endereço cadastrado"}), 400
        
        # 4. Preparar dados para o Mercado Pago
        mp_data = {
            "pedido_id": pedido_id,
            "cliente_email": usuario.email,
            "cliente_nome": usuario.nome,
            "cliente_sobrenome": usuario.sobrenome,
            "cliente_telefone": getattr(usuario, 'telefone', ''),
            "cep": endereco.cep,
            "cidade": endereco.cidade,
            "estado": endereco.estado,
            "logradouro": endereco.logradouro,
            "numero": endereco.numero,
            "itens": []
        }
        
        # 5. Adicionar itens do pedido
        valor_produtos = 0
        for item in itens:
            produto = Produto.query.get(item["produto_id"])
            if not produto:
                return jsonify({"erro": f"Produto {item['produto_id']} não encontrado"}), 404
                
            quantidade = int(item.get("quantidade", 1))
            subtotal = float(produto.preco) * quantidade
            valor_produtos += subtotal
            
            mp_data["itens"].append({
                "produto_id": produto.id,
                "nome": produto.nome,
                "descricao": produto.descricao or produto.nome,
                "quantidade": quantidade,
                "preco_unitario": float(produto.preco)
            })
        
        # 6. Adicionar frete se fornecido
        valor_total = valor_produtos
        if data.get("frete_valor") and data.get("frete_tipo"):
            frete_valor = float(data["frete_valor"])
            valor_total += frete_valor
            mp_data["frete_valor"] = frete_valor
            mp_data["frete_tipo"] = data["frete_tipo"]
        
        # 7. Criar preferência no Mercado Pago
        mp_service = MercadoPagoService()
        resultado_mp = mp_service.criar_preferencia(mp_data)
        
        if not resultado_mp["success"]:
            logging.error(f"Erro ao criar preferência MP: {resultado_mp.get('error')}")
            return jsonify({"erro": resultado_mp.get("error", "Erro ao criar pagamento")}), 400
        
        # 8. Resposta de sucesso
        resposta = {
            "success": True,
            "pedido_id": pedido_id,
            "valor_produtos": valor_produtos,
            "valor_total": valor_total,
            "pagamento": {
                "preference_id": resultado_mp["preference_id"],
                "init_point": resultado_mp["init_point"]
            }
        }
        
        # Adicionar link sandbox se disponível
        if resultado_mp.get("sandbox_init_point"):
            resposta["pagamento"]["sandbox_init_point"] = resultado_mp["sandbox_init_point"]
        
        logging.info(f"Pedido {pedido_id} criado com sucesso - Valor total: R$ {valor_total}")
        
        return jsonify(resposta), 201
        
    except ValueError as e:
        logging.error(f"Erro de validação: {str(e)}")
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        logging.error(f"Erro ao criar pedido completo: {str(e)}")
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

@checkout_bp.route('/test', methods=['GET'])
def test_integracoes():
    """Testa as integrações básicas"""
    try:
        resultados = {}
        
        # Testar Mercado Pago
        mp_token = os.getenv("MERCADO_PAGO_TOKEN")
        resultados["mercado_pago"] = {
            "configurado": bool(mp_token),
            "token_sandbox": bool(mp_token and mp_token.startswith("TEST-")),
            "token_length": len(mp_token) if mp_token else 0
        }
        
        # Testar Melhor Envio
        me_token = os.getenv("MELHOR_ENVIO_TOKEN")
        me_url = os.getenv("MELHOR_ENVIO_BASE_URL")
        resultados["melhor_envio"] = {
            "configurado": bool(me_token),
            "token_length": len(me_token) if me_token else 0,
            "url_sandbox": bool(me_url and "sandbox" in me_url)
        }
        
        # Testar dados da empresa
        resultados["empresa"] = {
            "cep_configurado": bool(os.getenv("EMPRESA_CEP")),
            "nome_configurado": bool(os.getenv("EMPRESA_NOME"))
        }
        
        return jsonify({
            "success": True,
            "integracoes": resultados
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "erro": str(e)
        }), 500

@checkout_bp.route('/test-frete', methods=['GET'])
def test_frete():
    """Teste rápido de cálculo de frete"""
    try:
        # Dados de teste
        origem = os.getenv("EMPRESA_CEP", "99700000")
        destino = "01310100"  # São Paulo - SP
        produtos = [{
            "quantidade": 1,
            "peso": 0.5,
            "altura": 10,
            "largura": 15,
            "comprimento": 20
        }]
        
        melhor_envio = MelhorEnvioService()
        resultado = melhor_envio.calcular_frete(origem, destino, produtos)
        
        return jsonify({
            "success": True,
            "teste": {
                "origem": origem,
                "destino": destino,
                "resultado": resultado
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "erro": str(e)
        }), 500