"""Motor de cálculo da Carteira Administrada."""

from typing import List

from engine.cdi import get_taxa_cdi_mensal
from models.cenario import CarteiraAdmin, ProjecaoCDI, ResumoCarteira


def simular_carteira_admin(
    carteira: CarteiraAdmin,
    projecao_cdi: ProjecaoCDI,
    janela_meses: int,
) -> tuple[List[float], ResumoCarteira]:
    """Simula a evolução mensal da carteira administrada.

    Modelo:
    - Rendimento líquido mensal = patrimônio × taxa_CDI_mensal × (target / 100)
    - Taxa admin mensal = patrimônio × (taxa_admin / 100 / 12)
    - Rendimento bruto = rendimento líquido + taxa admin
    - IR = 0

    Args:
        carteira: Parâmetros da carteira administrada.
        projecao_cdi: Projeção de CDI por ano.
        janela_meses: Duração da simulação em meses.

    Returns:
        Tupla com:
        - Lista de valores do patrimônio ao final de cada mês (índice 0 = mês 1)
        - Resumo financeiro da carteira
    """
    patrimonio = carteira.valor_investido
    target_fator = carteira.target_pct / 100.0
    taxa_admin_anual = carteira.taxa_admin_pct / 100.0

    evolucao = []
    total_rendimento_liquido = 0.0
    total_taxa_admin = 0.0

    for mes in range(1, janela_meses + 1):
        taxa_cdi_mensal = get_taxa_cdi_mensal(projecao_cdi.taxas_anuais, mes) / 100.0

        # Rendimento líquido (o que o investidor recebe)
        rendimento_liquido = patrimonio * taxa_cdi_mensal * target_fator

        # Taxa de administração (cobrada sobre patrimônio total)
        taxa_admin_mensal = patrimonio * (taxa_admin_anual / 12.0)

        # Patrimônio cresce pelo rendimento líquido
        patrimonio += rendimento_liquido

        # Acumuladores
        total_rendimento_liquido += rendimento_liquido
        total_taxa_admin += taxa_admin_mensal

        evolucao.append(patrimonio)

    # Rendimento bruto = líquido + taxa admin paga
    lucro_bruto = total_rendimento_liquido + total_taxa_admin

    resumo = ResumoCarteira(
        valor_inicial=carteira.valor_investido,
        valor_final=patrimonio,
        lucro_bruto=lucro_bruto,
        lucro_liquido=total_rendimento_liquido,
        ir_pago=0.0,
        taxa_admin_paga=total_taxa_admin,
    )

    return evolucao, resumo
