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


def criar_pedido_melhor_envio(pedido):
    """
    Cria pedido no Melhor Envio após pagamento aprovado
    """
    url = f"{MELHOR_ENVIO_API}/me/cart"

    payload = {
        "service": pedido.frete_tipo,  # ID do serviço escolhido
        "from": {
            "name": "Sua Empresa",
            "postal_code": EMPRESA_CEP,
        },
        "to": {
            "name": pedido.usuario.nome,
            "postal_code": pedido.endereco.cep,
            "address": pedido.endereco.logradouro,
            "number": pedido.endereco.numero,
        },
        "products": [
            {
                "name": item.produto.nome,
                "quantity": item.quantidade,
                "unitary_value": float(item.preco_unitario),
            }
            for item in pedido.itens
        ],
        "volumes": [
            {
                "height": max(i.altura for i in pedido.itens),
                "width": max(i.largura for i in pedido.itens),
                "length": max(i.comprimento for i in pedido.itens),
                "weight": sum(i.peso * i.quantidade for i in pedido.itens),
            }
        ],
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    return response.json()
