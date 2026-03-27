"""Funções para cálculo e projeção do CDI."""

from typing import List


def taxa_anual_para_mensal(taxa_anual_pct: float) -> float:
    """Converte taxa anual (%) para taxa mensal equivalente (%).

    Fórmula: (1 + taxa_anual)^(1/12) - 1

    Args:
        taxa_anual_pct: Taxa anual em % (ex: 14.0 para 14% a.a.)

    Returns:
        Taxa mensal equivalente em % (ex: ~1.0979 para 14% a.a.)
    """
    taxa_decimal = taxa_anual_pct / 100.0
    taxa_mensal = (1 + taxa_decimal) ** (1.0 / 12.0) - 1
    return taxa_mensal * 100.0


def get_taxa_cdi_anual(taxas_anuais: List[float], mes: int) -> float:
    """Retorna a taxa CDI anual para um dado mês da simulação.

    Args:
        taxas_anuais: Lista de taxas CDI anuais por ano (índice 0 = ano 1).
        mes: Mês da simulação (1-indexed).

    Returns:
        Taxa CDI anual em % para o mês solicitado.
    """
    if not taxas_anuais:
        return 0.0

    # Determina qual ano (0-indexed) corresponde ao mês
    ano_idx = (mes - 1) // 12

    # Se o mês está além das projeções, usa a última taxa disponível
    if ano_idx >= len(taxas_anuais):
        return taxas_anuais[-1]

    return taxas_anuais[ano_idx]


def get_taxa_cdi_mensal(taxas_anuais: List[float], mes: int) -> float:
    """Retorna a taxa CDI mensal equivalente para um dado mês.

    Args:
        taxas_anuais: Lista de taxas CDI anuais por ano.
        mes: Mês da simulação (1-indexed).

    Returns:
        Taxa CDI mensal em % para o mês solicitado.
    """
    taxa_anual = get_taxa_cdi_anual(taxas_anuais, mes)
    return taxa_anual_para_mensal(taxa_anual)
