from enum import Enum


class StatusPagamentoEnum(str, Enum):
    PENDENTE = "pending"
    APROVADO = "approved"
    AUTORIZADO = "authorized"
    EM_PROCESSAMENTO = "in_process"
    EM_MEDIACAO = "in_mediation"
    REJEITADO = "rejected"
    RECUSADO = "rejected"
    CANCELADO = "cancelled"
    REEMBOLSADO = "refunded"
    CHARGEBACK = "charged_back"
    ESTORNADO = "refunded"

    @classmethod
    def from_mercadopago(cls, status_mp: str):
        mapeamento = {
            "pending": cls.PENDENTE,
            "approved": cls.APROVADO,
            "authorized": cls.AUTORIZADO,
            "in_process": cls.EM_PROCESSAMENTO,
            "in_mediation": cls.EM_MEDIACAO,
            "rejected": cls.REJEITADO,
            "cancelled": cls.CANCELADO,
            "canceled": cls.CANCELADO,
            "refunded": cls.REEMBOLSADO,
            "charged_back": cls.CHARGEBACK,
        }

        status_lower = status_mp.lower() if status_mp else ""

        if status_lower in mapeamento:
            return mapeamento[status_lower]

        raise ValueError(
            f"Status '{status_mp}' não reconhecido. "
            f"Status válidos: {list(mapeamento.keys())}"
        )

    def __str__(self):
        return self.value
