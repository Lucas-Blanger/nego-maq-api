import os
import re
import json
import logging
import requests
from decimal import Decimal
from utils.crypto_utils import descriptografar_cpf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("melhor_envio")

MELHOR_ENVIO_API = os.getenv("MELHOR_ENVIO_API")
TOKEN = os.getenv("MELHOR_ENVIO_TOKEN")
EMPRESA_CEP = os.getenv("EMPRESA_CEP")


HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Aplicacao (contato@negomaq.com.br)",
}


def _only_digits(s):
    if not s:
        return None
    return re.sub(r"\D", "", s)


def _num(v):
    """Normaliza Decimal -> float, mantém int/float, tenta converter strings numéricas."""
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (int, float)):
        return v
    try:
        return float(v)
    except Exception:
        return v


def calcular_frete(from_postal_code, to_postal_code, weight, height, width, length):
    url = f"{MELHOR_ENVIO_API}/me/shipment/calculate"

    # Limpa e valida CEPs
    from_cep = _only_digits(str(from_postal_code))
    to_cep = _only_digits(str(to_postal_code))

    if not from_cep or len(from_cep) != 8 or not to_cep or len(to_cep) != 8:
        raise ValueError("CEPs inválidos para cálculo de frete")

    # Converter peso para kg (se peso já vier em gramas)
    weight_kg = _num(float(weight) / 1000 if float(weight) > 50 else float(weight))
    height = int(_num(height))
    width = int(_num(width))
    length = int(_num(length))

    # Validações básicas
    if weight_kg < 0.001:
        raise ValueError("Peso muito baixo")
    if weight_kg > 30:
        raise ValueError("Peso excede limite do Melhor Envio (30kg)")

    if height < 1 or width < 1 or length < 1:
        raise ValueError("Dimensões inválidas")
    if (height + width + length) > 200:
        raise ValueError("Soma das dimensões excede 200cm")

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
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        body = None
        try:
            body = resp.json()
        except Exception:
            body = resp.text if resp is not None else str(e)
        logger.error(
            "Melhor Envio calcular_frete error: %s %s",
            getattr(resp, "status_code", None),
            body,
        )
        raise ValueError(
            f"Melhor Envio calcular_frete: {getattr(resp, 'status_code', None)} - {body}"
        ) from e


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
    from_postal_code = EMPRESA_CEP or os.getenv("EMPRESA_CEP")
    to_postal_code = getattr(pedido.endereco, "cep", None)

    total_peso = sum(_num(i.peso) * int(i.quantidade) for i in pedido.itens)
    resultado_frete = calcular_frete(
        from_postal_code=from_postal_code,
        to_postal_code=to_postal_code,
        weight=total_peso,
        height=max(int(_num(i.altura)) for i in pedido.itens),
        width=max(int(_num(i.largura)) for i in pedido.itens),
        length=max(int(_num(i.comprimento)) for i in pedido.itens),
    )

    service_id = obter_id_servico_por_nome(pedido.frete_tipo, resultado_frete)

    # Recupera CPF do usuário associado ao pedido e normaliza
    usuario = getattr(pedido, "usuario", None)
    usuario_cpf_cript = getattr(usuario, "cpf", None) if usuario else None
    if not usuario_cpf_cript:
        raise ValueError("CPF do destinatário não encontrado no pedido")
    cpf = _only_digits(descriptografar_cpf(usuario_cpf_cript))

    # Monta volumes básicos a partir dos itens (um volume agregando todos os itens)
    volume = {
        "weight": _num(total_peso) / 1000.0,
        "length": int(_num(max(i.comprimento for i in pedido.itens))),
        "height": int(_num(max(i.altura for i in pedido.itens))),
        "width": int(_num(max(i.largura for i in pedido.itens))),
    }

    payload = {
        "from": {
            "postal_code": _only_digits(from_postal_code),
        },
        "to": {
            "postal_code": _only_digits(to_postal_code),
            "street": getattr(pedido.endereco, "logradouro", None) or "",
            "number": getattr(pedido.endereco, "numero", None) or "",
            "complement": getattr(pedido.endereco, "complemento", "") or "",
            "neighborhood": getattr(pedido.endereco, "bairro", "") or "",
            "city": getattr(pedido.endereco, "cidade", "") or "",
            "state": getattr(pedido.endereco, "estado", "") or "",
            "name": f"{getattr(usuario, 'nome', '')} {getattr(usuario, 'sobrenome', '')}".strip(),
            "phone": _only_digits(getattr(usuario, "telefone", None) or ""),
            "document": cpf,
        },
        "volumes": [volume],
        "services": [service_id],
    }

    try:
        url = f"{MELHOR_ENVIO_API}/me/cart"
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        body = None
        try:
            body = resp.json()
        except Exception:
            body = resp.text if resp is not None else str(e)
        logger.error(
            "Melhor Envio criar_pedido error: %s %s",
            getattr(resp, "status_code", None),
            body,
        )
        raise ValueError(
            f"Melhor Envio criar_pedido: {getattr(resp, 'status_code', None)} - {body}"
        ) from e


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
