"""Tabelas de resumo financeiro."""

import streamlit as st
import pandas as pd
from models.cenario import ResumoCarteira


def _fmt_brl(valor: float) -> str:
    """Formata valor em R$."""
    return f"R$ {valor:,.2f}"


def _fmt_pct(valor: float) -> str:
    """Formata percentual."""
    return f"{valor:.2f}%"


def render_resumo(resumo_admin: ResumoCarteira, resumo_diy: ResumoCarteira):
    """Renderiza tabela comparativa de resumo financeiro.

    Args:
        resumo_admin: Resumo da carteira administrada.
        resumo_diy: Resumo da carteira DIY.
    """
    st.subheader("📋 Resumo Financeiro")

    data = {
        "Métrica": [
            "Valor Investido",
            "Valor Final",
            "Lucro Bruto",
            "IR Pago",
            "Taxa Admin Paga",
            "Lucro Líquido",
            "Rentabilidade Líquida",
        ],
        "Carteira Administrada": [
            _fmt_brl(resumo_admin.valor_inicial),
            _fmt_brl(resumo_admin.valor_final),
            _fmt_brl(resumo_admin.lucro_bruto),
            _fmt_brl(resumo_admin.ir_pago),
            _fmt_brl(resumo_admin.taxa_admin_paga),
            _fmt_brl(resumo_admin.lucro_liquido),
            _fmt_pct(resumo_admin.rentabilidade_liquida_pct),
        ],
        "Carteira DIY": [
            _fmt_brl(resumo_diy.valor_inicial),
            _fmt_brl(resumo_diy.valor_final),
            _fmt_brl(resumo_diy.lucro_bruto),
            _fmt_brl(resumo_diy.ir_pago),
            _fmt_brl(resumo_diy.taxa_admin_paga),
            _fmt_brl(resumo_diy.lucro_liquido),
            _fmt_pct(resumo_diy.rentabilidade_liquida_pct),
        ],
    }

    df = pd.DataFrame(data)

    # Diferença entre DIY e Admin
    diff_liquido = resumo_diy.lucro_liquido - resumo_admin.lucro_liquido
    if diff_liquido > 0:
        st.success(f"✅ A Carteira DIY rende **{_fmt_brl(diff_liquido)}** a mais que a Administrada.")
    elif diff_liquido < 0:
        st.warning(f"⚠️ A Carteira Administrada rende **{_fmt_brl(abs(diff_liquido))}** a mais que a DIY.")
    else:
        st.info("🔄 Ambas as carteiras rendem o mesmo valor.")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )
