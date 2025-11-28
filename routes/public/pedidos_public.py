from flask import Blueprint, request, jsonify
from services.public.PedidosService import PedidoService
from services.public.PagamentosService import PagamentoService
from database.models.produto import Produto
from database.models.endereco import Endereco
from services.public.MelhorEnvioService import calcular_frete_pedido
from utils.middlewares.auth import token_required
import os

public_routes_pedidos = Blueprint("pedidos_public", __name__)


EMPRESA_CEP = os.getenv("EMPRESA_CEP")


# COTAÇÃO DE FRETE DO CARRINHO
@public_routes_pedidos.route("/frete/cotacao", methods=["POST"])
@token_required
def cotacao_frete_carrinho(payload):
    try:
        data = request.json
        usuario_id = data.get("usuario_id")
        endereco_id = data.get("endereco_id")
        itens_carrinho = data.get("itens", [])

        if not usuario_id:
            return jsonify({"erro": "usuario_id é obrigatório"}), 400

        if not itens_carrinho:
            return jsonify({"erro": "Nenhum item no carrinho"}), 400

        # Buscar endereço do usuário
        if endereco_id:
            endereco = Endereco.query.get(endereco_id)
            if not endereco:
                return jsonify({"erro": "Endereço não encontrado"}), 404
            if endereco.usuario_id != usuario_id:
                return jsonify({"erro": "Endereço não pertence ao usuário"}), 403
        else:
            # Pegar o primeiro endereço do usuário
            endereco = Endereco.query.filter_by(usuario_id=usuario_id).first()
            if not endereco:
                return jsonify({"erro": "Usuário não possui endereço cadastrado"}), 400

        cep_destino = endereco.cep

        # Buscar informações dos produtos
        itens_preparados = []
        for item in itens_carrinho:
            produto_id = item.get("produto_id")
            quantidade = item.get("quantidade", 1)

            produto = Produto.query.get(produto_id)
            if not produto:
                return jsonify({"erro": f"Produto {produto_id} não encontrado"}), 404

            itens_preparados.append(
                {
                    "peso": float(produto.peso) if produto.peso else 0,
                    "comprimento": (
                        int(produto.comprimento) if produto.comprimento else 0
                    ),
                    "altura": int(produto.altura) if produto.altura else 0,
                    "largura": int(produto.largura) if produto.largura else 0,
                    "quantidade": quantidade,
                }
            )

        # Calcular frete usando a API do Melhor Envio
        opcoes_frete = calcular_frete_pedido(
            cep_origem=EMPRESA_CEP, cep_destino=cep_destino, itens=itens_preparados
        )

        # Formatar resposta
        resultado = {
            "cep_origem": EMPRESA_CEP,
            "cep_destino": cep_destino,
            "opcoes": [],
        }

        # Processar e filtrar opções de frete
        for opcao in opcoes_frete:
            preco = float(opcao.get("price", 0))
            prazo_dias = opcao.get("delivery_time")

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
                    }
                )

        # Ordenar por preço
        resultado["opcoes"].sort(key=lambda x: x["preco"])

        if resultado["opcoes"]:
            resultado["opcao_mais_barata"] = resultado["opcoes"][0]
            resultado["opcao_mais_rapida"] = min(
                resultado["opcoes"], key=lambda x: x["prazo_dias"]
            )

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 400


# CRIAR UM NOVO PEDIDO (com frete já selecionado)
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


# OBTER PEDIDO
@public_routes_pedidos.route("/pedidos/<pedido_id>", methods=["GET"])
@token_required
def obter_pedido(payload, pedido_id):
    pedido = PedidoService.obter_pedido(pedido_id)
    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    return jsonify(pedido), 200


# PEDIDOS POR USUÁRIO
@public_routes_pedidos.route("/usuarios/<usuario_id>/pedidos", methods=["GET"])
@token_required
def pedidos_usuario(payload, usuario_id):
    pedidos_objs = PedidoService.listar_pedidos_usuario(usuario_id)

    # Converter cada objeto para dicionário
    pedidos = [
        {
            "pedido_id": p.id,
            "nome_usuario": p.usuario.nome if p.usuario else None,
            "sobrenome_usuario": p.usuario.sobrenome if p.usuario else None,
            "valor_total": float(p.valor_total),
            "status": p.status.value,
            "frete_valor": float(p.frete_valor) if p.frete_valor else None,
            "criado_em": (
                p.criado_em.isoformat()
                if hasattr(p, "criado_em") and p.criado_em
                else None
            ),
            "tem_rastreio": hasattr(p, "melhor_envio_id")
            and p.melhor_envio_id is not None,
        }
        for p in pedidos_objs
    ]

    return jsonify(pedidos), 200
