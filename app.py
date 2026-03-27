"""Simulador de Investimentos — Comparador de Carteiras.

Aplicação Streamlit para comparar Carteira Administrada vs Carteira DIY.
"""

import sys
from pathlib import Path

# Garante que o diretório raiz está no path
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from engine.carteira_admin import simular_carteira_admin
from engine.carteira_diy import simular_carteira_diy
from models.cenario import (
    CarteiraAdmin,
    CarteiraDIY,
    Cenario,
    ProjecaoCDI,
    Produto,
    TipoProduto,
)
from persistence.storage import (
    carregar_cenario,
    listar_cenarios,
    salvar_cenario,
)
from ui.charts import render_grafico_comparacao, render_grafico_evolucao
from ui.input_admin import render_input_admin
from ui.input_diy import render_input_diy
from ui.sidebar import get_cenario_ativo, render_sidebar
from ui.summary import render_resumo

# --- Configuração da página ---
st.set_page_config(
    page_title="Simulador de Investimentos",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("💰 Simulador de Investimentos")
st.caption("Compare Carteira Administrada vs Carteira DIY de Renda Fixa")


def _render_config_tab(cenario: Cenario):
    """Renderiza a aba de configuração do cenário."""

    # --- Parâmetros globais ---
    st.subheader("⚙️ Parâmetros Globais")
    col1, col2 = st.columns(2)

    with col1:
        janela = st.number_input(
            "Janela de investimento (meses)",
            min_value=1,
            max_value=360,
            value=cenario.janela_meses,
            step=6,
            key="janela_meses",
        )

    with col2:
        num_anos = max(1, (janela + 11) // 12)  # Arredonda para cima
        st.markdown(f"**Projeção CDI por ano** ({num_anos} ano{'s' if num_anos > 1 else ''})")

    # Projeção CDI
    taxas = list(cenario.projecao_cdi.taxas_anuais)
    # Ajusta o tamanho da lista
    while len(taxas) < num_anos:
        taxas.append(taxas[-1] if taxas else 14.0)
    taxas = taxas[:num_anos]

    cols_cdi = st.columns(min(num_anos, 5))
    for i in range(num_anos):
        with cols_cdi[i % len(cols_cdi)]:
            taxas[i] = st.number_input(
                f"Ano {i + 1} (% a.a.)",
                min_value=0.0,
                max_value=50.0,
                value=taxas[i],
                step=0.25,
                format="%.2f",
                key=f"cdi_ano_{i}",
            )

    st.divider()

    # --- Carteira Administrada ---
    admin = render_input_admin(cenario.carteira_admin)

    st.divider()

    # --- Carteira DIY ---
    diy = render_input_diy(cenario.carteira_diy, cenario)

    st.divider()

    # --- Botão salvar ---
    if st.button("💾 Salvar Cenário", type="primary", use_container_width=True):
        cenario_atualizado = Cenario(
            nome=cenario.nome,
            janela_meses=janela,
            projecao_cdi=ProjecaoCDI(taxas_anuais=taxas),
            carteira_admin=admin,
            carteira_diy=diy,
        )
        salvar_cenario(cenario_atualizado)
        st.success(f"Cenário '{cenario.nome}' salvo com sucesso!")
        st.rerun()


def _render_resultados_tab(cenario: Cenario):
    """Renderiza a aba de resultados do cenário ativo."""

    # Simular carteira administrada
    ev_admin, resumo_admin = simular_carteira_admin(
        cenario.carteira_admin,
        cenario.projecao_cdi,
        cenario.janela_meses,
    )

    # Simular carteira DIY
    ev_diy, resumo_diy = simular_carteira_diy(
        cenario.carteira_diy,
        cenario.projecao_cdi,
        cenario.janela_meses,
    )

    # Gráfico de evolução
    render_grafico_evolucao(ev_admin, ev_diy, cenario.nome)

    # Resumo financeiro
    render_resumo(resumo_admin, resumo_diy)


def _render_comparacao_tab():
    """Renderiza a aba de comparação de múltiplos cenários."""
    nomes = st.session_state.get("cenarios_comparar", [])

    if len(nomes) < 2:
        st.info("Selecione pelo menos 2 cenários na sidebar para comparar.")
        return

    resultados = {}
    resumos = {}

    for nome in nomes:
        cenario = carregar_cenario(nome)
        if cenario is None:
            continue

        ev_admin, resumo_admin = simular_carteira_admin(
            cenario.carteira_admin,
            cenario.projecao_cdi,
            cenario.janela_meses,
        )
        ev_diy, resumo_diy = simular_carteira_diy(
            cenario.carteira_diy,
            cenario.projecao_cdi,
            cenario.janela_meses,
        )

        resultados[nome] = (ev_admin, ev_diy)
        resumos[nome] = (resumo_admin, resumo_diy)

    # Gráfico comparativo
    render_grafico_comparacao(resultados)

    # Resumos lado a lado
    st.subheader("📋 Resumos Comparativos")
    for nome, (r_admin, r_diy) in resumos.items():
        with st.expander(f"📊 {nome}", expanded=True):
            render_resumo(r_admin, r_diy)


# ============================
# MAIN
# ============================

# Sidebar
render_sidebar()

# Conteúdo principal
cenario = get_cenario_ativo()

if cenario is None:
    st.info("👈 Crie um cenário na sidebar para começar.")
else:
    tab_config, tab_result, tab_compare = st.tabs([
        "⚙️ Configuração",
        "📈 Resultados",
        "📊 Comparação",
    ])

    with tab_config:
        _render_config_tab(cenario)

    with tab_result:
        _render_resultados_tab(cenario)

    with tab_compare:
        _render_comparacao_tab()
