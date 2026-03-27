"""Sidebar para gerenciamento de cenários."""

import streamlit as st
from persistence.storage import (
    carregar_cenario,
    carregar_todos_cenarios,
    deletar_cenario,
    listar_cenarios,
    salvar_cenario,
)
from models.cenario import (
    CarteiraAdmin,
    CarteiraDIY,
    Cenario,
    ProjecaoCDI,
)


def render_sidebar():
    """Renderiza a sidebar com gerenciamento de cenários."""
    st.sidebar.title("📁 Cenários")

    nomes = listar_cenarios()

    # --- Criar novo cenário ---
    st.sidebar.subheader("Novo Cenário")
    novo_nome = st.sidebar.text_input(
        "Nome do cenário",
        key="novo_cenario_nome",
        placeholder="Ex: Proposta XP Mar/2026",
    )
    if st.sidebar.button("➕ Criar Cenário", use_container_width=True):
        if novo_nome and novo_nome.strip():
            nome = novo_nome.strip()
            if nome in nomes:
                st.sidebar.error(f"Cenário '{nome}' já existe!")
            else:
                cenario = Cenario(
                    nome=nome,
                    projecao_cdi=ProjecaoCDI(taxas_anuais=[14.0, 14.0, 14.0]),
                    carteira_admin=CarteiraAdmin(valor_investido=100000.0),
                    carteira_diy=CarteiraDIY(produtos=[]),
                )
                salvar_cenario(cenario)
                st.session_state["cenario_ativo"] = nome
                st.rerun()
        else:
            st.sidebar.warning("Digite um nome para o cenário.")

    # --- Selecionar cenário ativo ---
    if nomes:
        st.sidebar.divider()
        st.sidebar.subheader("Cenário Ativo")

        cenario_ativo = st.session_state.get("cenario_ativo", nomes[0] if nomes else None)
        if cenario_ativo not in nomes:
            cenario_ativo = nomes[0] if nomes else None

        idx = nomes.index(cenario_ativo) if cenario_ativo in nomes else 0
        selecionado = st.sidebar.selectbox(
            "Selecione o cenário",
            nomes,
            index=idx,
            key="select_cenario",
        )
        st.session_state["cenario_ativo"] = selecionado

        # --- Deletar cenário ---
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("🗑️ Deletar", use_container_width=True):
                st.session_state["confirmar_delete"] = True

        if st.session_state.get("confirmar_delete"):
            with col2:
                if st.button("✅ Confirmar", use_container_width=True, type="primary"):
                    deletar_cenario(selecionado)
                    st.session_state.pop("confirmar_delete", None)
                    nomes_atualizado = listar_cenarios()
                    if nomes_atualizado:
                        st.session_state["cenario_ativo"] = nomes_atualizado[0]
                    else:
                        st.session_state.pop("cenario_ativo", None)
                    st.rerun()

    # --- Selecionar cenários para comparação ---
    if len(nomes) >= 2:
        st.sidebar.divider()
        st.sidebar.subheader("📊 Comparação")
        cenarios_comparar = st.sidebar.multiselect(
            "Cenários para comparar",
            nomes,
            default=nomes[:2],
            key="cenarios_comparar",
        )
        st.session_state["cenarios_comparar"] = cenarios_comparar


def get_cenario_ativo() -> Cenario | None:
    """Retorna o cenário ativo ou None."""
    nome = st.session_state.get("cenario_ativo")
    if nome:
        return carregar_cenario(nome)
    return None
