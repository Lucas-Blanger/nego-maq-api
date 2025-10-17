import os
import requests

MELHOR_ENVIO_API = os.getenv("MELHOR_ENVIO_API")
TOKEN = os.getenv("MELHOR_ENVIO_TOKEN")
EMPRESA_CEP = os.getenv("EMPRESA_CEP")


HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Aplicacao (contato@negomaq.com.br)",
}


def calcular_frete(from_postal_code, to_postal_code, weight, height, width, length):
    url = f"{MELHOR_ENVIO_API}/me/shipment/calculate"

    # Limpa e valida CEPs
    from_cep = str(from_postal_code).replace("-", "").strip()
    to_cep = str(to_postal_code).replace("-", "").strip()

    if len(from_cep) != 8 or len(to_cep) != 8:
        raise ValueError("CEPs devem ter 8 dígitos")

    # Converter peso para kg
    weight_kg = float(weight) / 1000

    # Validações básicas
    if weight_kg < 0.001:
        raise ValueError("Peso mínimo: 1 grama")
    if weight_kg > 30:
        raise ValueError("Peso máximo: 30 kg")

    height = int(height)
    width = int(width)
    length = int(length)

    # Dimensões mínimas
    if height < 1 or width < 1 or length < 1:
        raise ValueError("Dimensões mínimas: 1 cm")

    # Soma das dimensões não pode exceder 200cm
    if (height + width + length) > 200:
        raise ValueError("Soma das dimensões não pode exceder 200 cm")

    payload = {
        "from": {"postal_code": from_cep},
        "to": {"postal_code": to_cep},
        "package": {
            "weight": weight_kg,
            "width": width,
            "height": height,
            "length": length,
        },
    }

    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"Erro HTTP: {e}")
        print(f"Response body: {response.text}")
        raise


def calcular_frete_pedido(cep_origem, cep_destino, itens):
    """
    Calcula o frete para múltiplos itens de um pedido.

    Args:
        cep_origem: CEP de origem
        cep_destino: CEP de destino
        itens: Lista de dicts com {peso, altura, largura, comprimento, quantidade}

    Returns:
        Lista de opções de frete disponíveis
    """
    peso_total = sum(item["peso"] * item["quantidade"] for item in itens)

    altura_max = max(item["altura"] for item in itens)
    largura_max = max(item["largura"] for item in itens)
    comprimento_max = max(item["comprimento"] for item in itens)

    return calcular_frete(
        from_postal_code=cep_origem,
        to_postal_code=cep_destino,
        weight=peso_total,
        height=altura_max,
        width=largura_max,
        length=comprimento_max,
    )


def listar_transportadoras():
    url = f"{MELHOR_ENVIO_API}/me/shipment/agencies"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def obter_id_servico_por_nome(nome_servico, resultado_calculo):
    nome_servico = nome_servico.strip().upper()

    for opcao in resultado_calculo:
        nome_api = opcao.get("name", "").upper()
        if nome_servico in nome_api:
            return opcao["id"]

    raise ValueError(
        f"Serviço '{nome_servico}' não encontrado no resultado do cálculo."
    )


def criar_pedido_melhor_envio(pedido):
    """
    Cria pedido no carrinho do Melhor Envio usando apenas o nome do frete
    e retorna o ID e protocolo do pedido.
    """
    from_postal_code = os.getenv("EMPRESA_CEP")
    to_postal_code = pedido.endereco.cep

    resultado_frete = calcular_frete(
        from_postal_code=from_postal_code,
        to_postal_code=to_postal_code,
        weight=sum(i.peso * i.quantidade for i in pedido.itens),
        height=max(i.altura for i in pedido.itens),
        width=max(i.largura for i in pedido.itens),
        length=max(i.comprimento for i in pedido.itens),
    )

    service_id = obter_id_servico_por_nome(pedido.frete_tipo, resultado_frete)

    payload = {
        "service": service_id,
        "from": {
            "name": os.getenv("EMPRESA_NOME"),
            "phone": os.getenv("EMPRESA_TELEFONE"),
            "email": os.getenv("EMPRESA_EMAIL"),
            "company_document": os.getenv("EMPRESA_CNPJ"),
            "address": os.getenv("EMPRESA_ENDERECO"),
            "number": os.getenv("EMPRESA_NUMERO"),
            "district": os.getenv("EMPRESA_BAIRRO"),
            "city": os.getenv("EMPRESA_CIDADE"),
            "state_abbr": os.getenv("EMPRESA_ESTADO"),
            "postal_code": from_postal_code,
        },
        "to": {
            "name": pedido.usuario.nome,
            "phone": pedido.usuario.telefone,
            "email": pedido.usuario.email,
            "document": pedido.usuario.cpf or "00000000000",
            "address": pedido.endereco.logradouro,
            "number": pedido.endereco.numero,
            "district": pedido.endereco.bairro,
            "city": pedido.endereco.cidade,
            "state_abbr": pedido.endereco.estado,
            "postal_code": pedido.endereco.cep,
        },
        "products": [
            {
                "name": item.produto.nome,
                "quantity": int(item.quantidade),
                "unitary_value": float(item.preco_unitario),
                "weight": float(item.peso),
                "width": float(item.largura),
                "height": float(item.altura),
                "length": float(item.comprimento),
            }
            for item in pedido.itens
        ],
    }

    url = f"{MELHOR_ENVIO_API}/me/cart"
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()

    pedido.melhor_envio_id = data.get("id")
    pedido.melhor_envio_protocolo = data.get("protocol")

    return {
        "melhor_envio_id": pedido.melhor_envio_id,
        "protocol": pedido.melhor_envio_protocolo,
    }


def comprar_envio(order_id):
    """Compra o envio"""
    url = f"{MELHOR_ENVIO_API}/me/shipment/checkout"
    response = requests.post(url, headers=HEADERS, json={"orders": [order_id]})
    response.raise_for_status()
    return response.json()


def gerar_etiqueta(order_id):
    """Gera a etiqueta de envio"""
    url = f"{MELHOR_ENVIO_API}/me/shipment/generate"
    response = requests.post(url, headers=HEADERS, json={"orders": [order_id]})
    response.raise_for_status()
    return response.json()


def imprimir_etiqueta(order_id):
    """Retorna o link de impressão da etiqueta"""
    url = f"{MELHOR_ENVIO_API}/me/shipment/print"
    response = requests.post(url, headers=HEADERS, json={"orders": [order_id]})
    response.raise_for_status()
    data = response.json()
    return data.get("url")
