import os
import re
import logging
import requests
from decimal import Decimal
from utils.crypto_utils import descriptografar_cpf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("melhor_envio")

MELHOR_ENVIO_API = os.getenv("MELHOR_ENVIO_API")
TOKEN = os.getenv("MELHOR_ENVIO_TOKEN")
EMPRESA_CEP = os.getenv("EMPRESA_CEP")
EMPRESA_NOME = os.getenv("EMPRESA_NOME")
EMPRESA_ENDERECO = os.getenv("EMPRESA_ENDERECO")
EMPRESA_NUMERO = os.getenv("EMPRESA_NUMERO")
EMPRESA_BAIRRO = os.getenv("EMPRESA_BAIRRO")
EMPRESA_CIDADE = os.getenv("EMPRESA_CIDADE")
EMPRESA_ESTADO = os.getenv("EMPRESA_ESTADO")
EMPRESA_TELEFONE = os.getenv("EMPRESA_TELEFONE")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Aplicacao (contato@negomaq.com.br)",
}


def _only_digits(s):
    """Remove tudo que não é dígito"""
    if not s:
        return None
    return re.sub(r"\D", "", s)


def _num(v):
    """
    Normaliza valores numéricos para float.
    Decimal -> float, mantém int/float, converte strings.
    """
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        v = v.replace(",", ".")
    try:
        return float(v)
    except Exception:
        return v


def calcular_frete(from_postal_code, to_postal_code, weight, height, width, length):
    """
    Calcula frete usando a API do Melhor Envio.

    Args:
        from_postal_code: CEP origem
        to_postal_code: CEP destino
        weight: Peso em GRAMAS
        height: Altura em CM
        width: Largura em CM
        length: Comprimento em CM

    Returns:
        Lista de opções de frete com todos os dados necessários
    """
    url = f"{MELHOR_ENVIO_API}/me/shipment/calculate"

    # Limpar e validar CEPs
    from_cep = _only_digits(str(from_postal_code))
    to_cep = _only_digits(str(to_postal_code))

    if not from_cep or len(from_cep) != 8 or not to_cep or len(to_cep) != 8:
        raise ValueError("CEPs inválidos para cálculo de frete")

    # Converter peso de GRAMAS para KG
    weight_gramas = float(_num(weight))
    weight_kg = weight_gramas / 1000.0

    # Garantir que dimensões são inteiros
    height = int(_num(height))
    width = int(_num(width))
    length = int(_num(length))

    # Validações
    if weight_kg < 0.001:
        raise ValueError("Peso muito baixo (mínimo: 1g)")
    if weight_kg > 30:
        raise ValueError("Peso excede limite do Melhor Envio (30kg)")
    if height < 1 or width < 1 or length < 1:
        raise ValueError("Dimensões inválidas (mínimo: 1cm)")
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
            "Erro ao calcular frete: %s - %s",
            getattr(resp, "status_code", None),
            body,
        )
        raise ValueError(
            f"Erro no Melhor Envio: {getattr(resp, 'status_code', None)} - {body}"
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
    if not itens or len(itens) == 0:
        raise ValueError("Nenhum item fornecido para cálculo de frete")

    # Somar peso total (peso * quantidade de cada item)
    peso_total = sum(_num(item["peso"]) * int(item["quantidade"]) for item in itens)

    # Pegar as maiores dimensões entre todos os itens
    altura_max = max(_num(item["altura"]) for item in itens)
    largura_max = max(_num(item["largura"]) for item in itens)
    comprimento_max = max(_num(item["comprimento"]) for item in itens)

    return calcular_frete(
        from_postal_code=cep_origem,
        to_postal_code=cep_destino,
        weight=peso_total,
        height=altura_max,
        width=largura_max,
        length=comprimento_max,
    )


def criar_pedido_melhor_envio(pedido):
    """
    Cria pedido no carrinho do Melhor Envio.
    Usa o frete_servico_id salvo no pedido (obtido durante a cotação).

    O pedido DEVE ter:
    - frete_servico_id: ID do serviço escolhido (OBRIGATÓRIO)
    - frete_valor: Valor cotado
    - frete_tipo: Nome da transportadora
    - frete_servico_nome: Nome do serviço

    Returns:
        {
            "melhor_envio_id": "xxx",
            "protocol": "ORD-xxx",
            "service_name": "SEDEX",
            "price": 69.87
        }
    """
    from_postal_code = EMPRESA_CEP
    to_postal_code = getattr(pedido.endereco, "cep", None)

    if not to_postal_code:
        raise ValueError("CEP de destino não encontrado no pedido")

    if not pedido.itens or len(pedido.itens) == 0:
        raise ValueError("Pedido não possui itens")

    service_id = getattr(pedido, "frete_servico_id", None)

    if not service_id:
        raise ValueError(
            "ID do serviço de frete não encontrado. "
            "Certifique-se de que 'frete_servico_id' foi salvo ao criar o pedido."
        )

    logger.info(
        f"Criando envio para pedido #{pedido.id}: "
        f"{pedido.frete_servico_nome or pedido.frete_tipo} (ID: {service_id})"
    )

    # Calcular peso total
    total_peso = sum(_num(i.peso) * int(i.quantidade) for i in pedido.itens)

    # Recuperar e validar CPF do usuário
    usuario = getattr(pedido, "usuario", None)
    if not usuario:
        raise ValueError("Usuário não encontrado no pedido")

    usuario_cpf_cript = getattr(usuario, "cpf", None)
    if not usuario_cpf_cript:
        raise ValueError("CPF do destinatário não encontrado")

    cpf = _only_digits(descriptografar_cpf(usuario_cpf_cript))
    if not cpf or len(cpf) != 11:
        raise ValueError("CPF inválido do destinatário")

    # Validar endereço
    if not pedido.endereco:
        raise ValueError("Endereço de destino não encontrado")

    # Validar CEP
    to_cep_limpo = _only_digits(to_postal_code)
    if not to_cep_limpo or len(to_cep_limpo) != 8:
        raise ValueError(f"CEP de destino inválido: {to_postal_code}")

    # Validar estado
    estado = getattr(pedido.endereco, "estado", "")
    estados_validos = [
        "AC",
        "AL",
        "AP",
        "AM",
        "BA",
        "CE",
        "DF",
        "ES",
        "GO",
        "MA",
        "MT",
        "MS",
        "MG",
        "PA",
        "PB",
        "PR",
        "PE",
        "PI",
        "RJ",
        "RN",
        "RS",
        "RO",
        "RR",
        "SC",
        "SP",
        "SE",
        "TO",
    ]
    if not estado or estado.upper() not in estados_validos:
        raise ValueError(f"Estado inválido: {estado}. Use a sigla (ex: SP, RJ)")

    # Preparar produtos
    products = []
    for item in pedido.itens:
        products.append(
            {
                "name": item.produto.nome[:50],
                "quantity": int(item.quantidade),
                "unitary_value": round(float(_num(item.preco_unitario)), 2),
            }
        )

    # Montar payload
    payload = {
        "service": service_id,
        "from": {
            "name": EMPRESA_NOME,
            "postal_code": _only_digits(from_postal_code),
            "address": EMPRESA_ENDERECO,
            "number": EMPRESA_NUMERO,
            "district": EMPRESA_BAIRRO,
            "city": EMPRESA_CIDADE,
            "state_abbr": EMPRESA_ESTADO,
            "phone": _only_digits(EMPRESA_TELEFONE),
        },
        "to": {
            "name": f"{getattr(usuario, 'nome', '')} {getattr(usuario, 'sobrenome', '')}".strip(),
            "postal_code": to_cep_limpo,
            "address": getattr(pedido.endereco, "logradouro", "") or "",
            "number": str(getattr(pedido.endereco, "numero", "") or "S/N"),
            "complement": getattr(pedido.endereco, "complemento", "") or "",
            "district": getattr(pedido.endereco, "bairro", "") or "",
            "city": getattr(pedido.endereco, "cidade", "") or "",
            "state_abbr": estado.upper(),
            "phone": _only_digits(getattr(usuario, "telefone", None) or ""),
            "document": cpf,
        },
        "products": products,
        "volumes": [
            {
                "height": int(_num(max(i.altura for i in pedido.itens))),
                "width": int(_num(max(i.largura for i in pedido.itens))),
                "length": int(_num(max(i.comprimento for i in pedido.itens))),
                "weight": round(float(_num(total_peso) / 1000.0), 3),  # kg
            }
        ],
        "options": {
            "insurance_value": round(float(_num(pedido.valor_total)), 2),
            "receipt": False,
            "own_hand": False,
            "collect": False,
        },
    }

    try:
        url = f"{MELHOR_ENVIO_API}/me/cart"
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=20)
        resp.raise_for_status()

        result = resp.json()

        # Extrair dados da resposta
        if isinstance(result, dict):
            order_id = result.get("id")
            protocol = result.get("protocol")
            service_name = result.get("service_name") or result.get("name", "")
            price = result.get("price", 0)
        else:
            # Se retornar lista, pegar primeiro item
            order_id = result[0].get("id") if result else None
            protocol = result[0].get("protocol") if result else None
            service_name = (
                result[0].get("service_name") or result[0].get("name", "")
                if result
                else ""
            )
            price = result[0].get("price", 0) if result else 0

        if not order_id:
            raise ValueError(f"ID do pedido não retornado pela API: {result}")

        # Fallback para nome do serviço
        if not service_name:
            service_name = (
                pedido.frete_servico_nome or pedido.frete_tipo or "Serviço de entrega"
            )

        preco_cotado = Decimal(str(pedido.frete_valor))
        preco_real = Decimal(str(price))
        diferenca = preco_real - preco_cotado

        # Avisar se houver diferença significativa
        if abs(diferenca) > Decimal("0.50"):
            logger.warning(
                f"Diferença de preço no pedido #{pedido.id}:\n"
                f"  Cotado: R$ {float(preco_cotado):.2f}\n"
                f"  Real: R$ {float(preco_real):.2f}\n"
                f"  Diferença: R$ {float(abs(diferenca)):.2f}"
            )

        logger.info(
            f"Pedido Melhor Envio criado: {protocol} | "
            f"Serviço: {service_name} | R$ {float(preco_real):.2f}"
        )

        return {
            "melhor_envio_id": order_id,
            "protocol": protocol,
            "service_name": service_name,
            "price": float(price),  # Converter para float para JSON
        }

    except requests.exceptions.HTTPError as e:
        body = None
        try:
            body = resp.json()
        except Exception:
            body = resp.text if resp is not None else str(e)
        logger.error(
            "Erro ao criar pedido Melhor Envio: %s - %s",
            getattr(resp, "status_code", None),
            body,
        )
        raise ValueError(
            f"Erro no Melhor Envio: {getattr(resp, 'status_code', None)} - {body}"
        ) from e


def comprar_envio(order_id):
    """Compra o envio (checkout)"""
    url = f"{MELHOR_ENVIO_API}/me/shipment/checkout"
    try:
        response = requests.post(
            url, headers=HEADERS, json={"orders": [order_id]}, timeout=20
        )
        response.raise_for_status()
        logger.info(f"Envio #{order_id} comprado com sucesso")
        return response.json()
    except requests.exceptions.HTTPError as e:
        body = response.text if response else str(e)
        logger.error(f"Erro ao comprar envio #{order_id}: {body}")
        raise


def gerar_etiqueta(order_id):
    """Gera a etiqueta de envio"""
    url = f"{MELHOR_ENVIO_API}/me/shipment/generate"
    try:
        response = requests.post(
            url, headers=HEADERS, json={"orders": [order_id]}, timeout=20
        )
        response.raise_for_status()
        logger.info(f"Etiqueta gerada para envio #{order_id}")
        return response.json()
    except requests.exceptions.HTTPError as e:
        body = response.text if response else str(e)
        logger.error(f"Erro ao gerar etiqueta #{order_id}: {body}")
        raise


def imprimir_etiqueta(order_id):
    """Retorna o link de impressão da etiqueta"""
    url = f"{MELHOR_ENVIO_API}/me/shipment/print"
    try:
        response = requests.post(
            url, headers=HEADERS, json={"orders": [order_id]}, timeout=20
        )
        response.raise_for_status()
        data = response.json()
        url_etiqueta = data.get("url")
        logger.info(f"Link da etiqueta #{order_id}: {url_etiqueta}")
        return url_etiqueta
    except requests.exceptions.HTTPError as e:
        body = response.text if response else str(e)
        logger.error(f"Erro ao imprimir etiqueta #{order_id}: {body}")
        raise


def listar_transportadoras():
    # Lista transportadoras disponíveis
    url = f"{MELHOR_ENVIO_API}/me/shipment/agencies"
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return response.json()
