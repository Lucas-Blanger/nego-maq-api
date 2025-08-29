from enum import Enum


class StatusPagamentoEnum(Enum):
    PENDENTE = "Pendente"
    APROVADO = "Aprovado"
    RECUSADO = "Recusado"
    ESTORNADO = "Estornado"
