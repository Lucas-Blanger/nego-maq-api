from enum import Enum


class StatusPedidoEnum(Enum):
    PENDENTE = "PENDENTE"
    PAGO = "PAGO"
    EM_SEPARACAO = "EM_SEPARACAO"
    ENVIADO = "ENVIADO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"
