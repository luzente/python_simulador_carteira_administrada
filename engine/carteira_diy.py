"""Motor de cálculo da Carteira DIY."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from engine.cdi import get_taxa_cdi_mensal
from engine.ir import calcular_ir, meses_para_dias
from models.cenario import CarteiraDIY, Produto, ProjecaoCDI, ResumoCarteira


@dataclass
class _ProdutoAtivo:
    """Estado interno de um produto durante a simulação."""
    produto: Produto
    valor_atual: float
    valor_no_inicio_ciclo: float  # Valor no início do ciclo atual (para cálculo de rendimento)
    meses_no_ciclo: int = 0       # Meses desde o início/reinvestimento
    meses_restantes: int = 0      # Meses até vencimento

    @classmethod
    def from_produto(cls, produto: Produto) -> '_ProdutoAtivo':
        return cls(
            produto=produto,
            valor_atual=produto.valor,
            valor_no_inicio_ciclo=produto.valor,
            meses_no_ciclo=0,
            meses_restantes=produto.prazo_meses,
        )


def simular_carteira_diy(
    carteira: CarteiraDIY,
    projecao_cdi: ProjecaoCDI,
    janela_meses: int,
) -> tuple[List[float], ResumoCarteira]:
    """Simula a evolução mensal da carteira DIY.

    Modelo por produto:
    - Rendimento mensal = valor_atual × taxa_CDI_mensal × (taxa_produto / 100)
    - No vencimento:
        - CDB: IR sobre rendimento do ciclo, reinveste líquido em produto idêntico
        - LCI/LCA: Sem IR, reinveste bruto em produto idêntico
    - No mês final da janela: liquida todos os produtos

    Args:
        carteira: Carteira DIY com lista de produtos.
        projecao_cdi: Projeção de CDI por ano.
        janela_meses: Duração da simulação em meses.

    Returns:
        Tupla com:
        - Lista de valores do patrimônio total ao final de cada mês
        - Resumo financeiro da carteira
    """
    if not carteira.produtos:
        evolucao = [0.0] * janela_meses
        return evolucao, ResumoCarteira(
            valor_inicial=0.0,
            valor_final=0.0,
            lucro_bruto=0.0,
            lucro_liquido=0.0,
            ir_pago=0.0,
            taxa_admin_paga=0.0,
        )

    # Inicializa produtos ativos
    ativos: List[_ProdutoAtivo] = [
        _ProdutoAtivo.from_produto(p) for p in carteira.produtos
    ]

    valor_inicial_total = sum(p.valor for p in carteira.produtos)
    evolucao = []
    total_ir_pago = 0.0
    total_rendimento_bruto = 0.0

    for mes in range(1, janela_meses + 1):
        taxa_cdi_mensal = get_taxa_cdi_mensal(projecao_cdi.taxas_anuais, mes) / 100.0
        is_ultimo_mes = (mes == janela_meses)

        for ativo in ativos:
            taxa_produto = ativo.produto.taxa_cdi / 100.0

            # Rendimento do mês
            rendimento_mes = ativo.valor_atual * taxa_cdi_mensal * taxa_produto
            ativo.valor_atual += rendimento_mes
            ativo.meses_no_ciclo += 1
            ativo.meses_restantes -= 1

            total_rendimento_bruto += rendimento_mes

            # Verifica vencimento ou fim da janela
            venceu = ativo.meses_restantes <= 0
            deve_liquidar = venceu or is_ultimo_mes

            if deve_liquidar:
                # Calcula rendimento acumulado neste ciclo
                rendimento_ciclo = ativo.valor_atual - ativo.valor_no_inicio_ciclo
                dias_ciclo = meses_para_dias(ativo.meses_no_ciclo)

                if not ativo.produto.is_isento_ir() and rendimento_ciclo > 0:
                    ir = calcular_ir(rendimento_ciclo, dias_ciclo)
                    total_ir_pago += ir
                    ativo.valor_atual -= ir

                # Se venceu antes do fim e não é o último mês, reinveste
                if venceu and not is_ultimo_mes:
                    ativo.valor_no_inicio_ciclo = ativo.valor_atual
                    ativo.meses_no_ciclo = 0
                    ativo.meses_restantes = ativo.produto.prazo_meses

        # Patrimônio total ao final do mês
        patrimonio_total = sum(a.valor_atual for a in ativos)
        evolucao.append(patrimonio_total)

    valor_final = sum(a.valor_atual for a in ativos)
    lucro_liquido = valor_final - valor_inicial_total
    lucro_bruto = total_rendimento_bruto

    resumo = ResumoCarteira(
        valor_inicial=valor_inicial_total,
        valor_final=valor_final,
        lucro_bruto=lucro_bruto,
        lucro_liquido=lucro_liquido,
        ir_pago=total_ir_pago,
        taxa_admin_paga=0.0,
    )

    return evolucao, resumo
