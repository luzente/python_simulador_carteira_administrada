"""Gráficos de evolução patrimonial com Plotly."""

from typing import Dict, List, Tuple

import plotly.graph_objects as go
import streamlit as st

from models.cenario import ResumoCarteira


def render_grafico_evolucao(
    evolucao_admin: List[float],
    evolucao_diy: List[float],
    cenario_nome: str,
):
    """Renderiza gráfico de evolução mensal: Administrada vs DIY.

    Args:
        evolucao_admin: Valores mensais da carteira administrada.
        evolucao_diy: Valores mensais da carteira DIY.
        cenario_nome: Nome do cenário (para título).
    """
    meses = list(range(1, len(evolucao_admin) + 1))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=meses,
        y=evolucao_admin,
        name="Carteira Administrada",
        mode="lines",
        line=dict(color="#636EFA", width=2.5),
        hovertemplate="Mês %{x}<br>R$ %{y:,.2f}<extra>Administrada</extra>",
    ))

    fig.add_trace(go.Scatter(
        x=meses,
        y=evolucao_diy,
        name="Carteira DIY",
        mode="lines",
        line=dict(color="#00CC96", width=2.5),
        hovertemplate="Mês %{x}<br>R$ %{y:,.2f}<extra>DIY</extra>",
    ))

    fig.update_layout(
        title=f"📈 Evolução Patrimonial — {cenario_nome}",
        xaxis_title="Mês",
        yaxis_title="Patrimônio (R$)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(tickformat=",.0f", tickprefix="R$ "),
        template="plotly_white",
        height=500,
    )

    st.plotly_chart(fig, use_container_width=True)  # type: ignore[call-arg]


def render_grafico_comparacao(
    resultados: Dict[str, Tuple[List[float], List[float]]],
):
    """Renderiza gráfico de comparação de múltiplos cenários.

    Args:
        resultados: Dict de {nome_cenario: (evolucao_admin, evolucao_diy)}
    """
    if not resultados:
        st.info("Selecione cenários na sidebar para comparar.")
        return

    fig = go.Figure()

    cores_admin = ["#636EFA", "#AB63FA", "#FFA15A", "#19D3F3", "#FF6692"]
    cores_diy = ["#00CC96", "#B6E880", "#FECB52", "#FF97FF", "#EF553B"]

    for i, (nome, (ev_admin, ev_diy)) in enumerate(resultados.items()):
        meses = list(range(1, len(ev_admin) + 1))
        cor_admin = cores_admin[i % len(cores_admin)]
        cor_diy = cores_diy[i % len(cores_diy)]

        fig.add_trace(go.Scatter(
            x=meses,
            y=ev_admin,
            name=f"{nome} — Admin",
            mode="lines",
            line=dict(color=cor_admin, width=2),
            hovertemplate=f"Mês %{{x}}<br>R$ %{{y:,.2f}}<extra>{nome} Admin</extra>",
        ))
        fig.add_trace(go.Scatter(
            x=meses,
            y=ev_diy,
            name=f"{nome} — DIY",
            mode="lines",
            line=dict(color=cor_diy, width=2, dash="dash"),
            hovertemplate=f"Mês %{{x}}<br>R$ %{{y:,.2f}}<extra>{nome} DIY</extra>",
        ))

    fig.update_layout(
        title="📊 Comparação de Cenários",
        xaxis_title="Mês",
        yaxis_title="Patrimônio (R$)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(tickformat=",.0f", tickprefix="R$ "),
        template="plotly_white",
        height=550,
    )

    st.plotly_chart(fig, use_container_width=True)
