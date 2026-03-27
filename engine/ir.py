"""Cálculo do Imposto de Renda pela tabela regressiva."""


# Tabela regressiva de IR para renda fixa (CDB, etc.)
# (limite_dias_inclusive, aliquota_pct)
TABELA_REGRESSIVA_IR = [
    (180, 22.5),    # Até 180 dias: 22,5%
    (360, 20.0),    # De 181 a 360 dias: 20%
    (720, 17.5),    # De 361 a 720 dias: 17,5%
    (float('inf'), 15.0),  # Acima de 720 dias: 15%
]


def aliquota_ir(dias: int) -> float:
    """Retorna a alíquota de IR baseada na tabela regressiva.

    Args:
        dias: Número de dias corridos do investimento.

    Returns:
        Alíquota em % (ex: 22.5, 20.0, 17.5, 15.0).
    """
    for limite, aliquota in TABELA_REGRESSIVA_IR:
        if dias <= limite:
            return aliquota
    return 15.0  # Fallback (nunca deve chegar aqui)


def calcular_ir(rendimento: float, dias: int) -> float:
    """Calcula o valor do IR sobre o rendimento.

    Args:
        rendimento: Valor do rendimento (lucro) em R$.
        dias: Número de dias corridos do investimento.

    Returns:
        Valor do IR em R$.
    """
    if rendimento <= 0:
        return 0.0

    taxa = aliquota_ir(dias) / 100.0
    return rendimento * taxa


def meses_para_dias(meses: int) -> int:
    """Converte meses em dias corridos (aproximação de 30 dias/mês).

    Args:
        meses: Número de meses.

    Returns:
        Número aproximado de dias corridos.
    """
    return meses * 30
