"""Formulário de entrada da Carteira Administrada."""

import streamlit as st
from models.cenario import CarteiraAdmin


def render_input_admin(admin: CarteiraAdmin) -> CarteiraAdmin:
    """Renderiza os campos de entrada da carteira administrada.

    Args:
        admin: Dados atuais da carteira administrada.

    Returns:
        CarteiraAdmin atualizado com os valores do formulário.
    """
    st.subheader("🏦 Carteira Administrada")

    col1, col2, col3 = st.columns(3)

    with col1:
        valor = st.number_input(
            "Valor investido (R$)",
            min_value=0.0,
            value=admin.valor_investido,
            step=1000.0,
            format="%.2f",
            key="admin_valor",
        )

    with col2:
        target = st.number_input(
            "Target (% do CDI líquido)",
            min_value=0.0,
            max_value=200.0,
            value=admin.target_pct,
            step=0.5,
            format="%.1f",
            key="admin_target",
            help="Percentual do CDI que a carteira entrega líquido. Ex: 97 = 97% do CDI.",
        )

    with col3:
        taxa_admin = st.number_input(
            "Taxa de administração (% a.a.)",
            min_value=0.0,
            max_value=10.0,
            value=admin.taxa_admin_pct,
            step=0.1,
            format="%.2f",
            key="admin_taxa",
            help="Taxa cobrada sobre o patrimônio total, por ano.",
        )

    return CarteiraAdmin(
        valor_investido=valor,
        target_pct=target,
        taxa_admin_pct=taxa_admin,
    )
