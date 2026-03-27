"""Formulário de entrada da Carteira DIY."""

import streamlit as st
import pandas as pd
from models.cenario import CarteiraDIY, Cenario, Produto, TipoProduto
from persistence.storage import salvar_cenario


def render_input_diy(diy: CarteiraDIY, cenario: Cenario) -> CarteiraDIY:
    """Renderiza os campos de entrada da carteira DIY.

    Args:
        diy: Dados atuais da carteira DIY.
        cenario: Cenário completo (para salvar ao adicionar/remover produtos).

    Returns:
        CarteiraDIY atualizado com os valores do formulário.
    """
    st.subheader("🛠️ Carteira DIY")

    # Editor de produtos
    if diy.produtos:
        dados = [
            {
                "Nome": p.nome,
                "Tipo": p.tipo.value,
                "Taxa (% CDI)": p.taxa_cdi,
                "Valor (R$)": p.valor,
                "Prazo (meses)": p.prazo_meses,
            }
            for p in diy.produtos
        ]
    else:
        dados = []

    st.markdown("**Produtos da carteira:**")

    # Adicionar novo produto
    with st.expander("➕ Adicionar produto", expanded=not bool(dados)):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do produto", placeholder="Ex: CDB Banco X", key="diy_novo_nome")
            tipo = st.selectbox("Tipo", ["CDB", "LCI", "LCA"], key="diy_novo_tipo")
            taxa = st.number_input("Taxa (% do CDI)", min_value=0.0, max_value=200.0,
                                   value=100.0, step=1.0, key="diy_novo_taxa",
                                   help="Ex: 110 = 110% do CDI")
        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.0, value=10000.0,
                                    step=1000.0, format="%.2f", key="diy_novo_valor")
            prazo = st.number_input("Prazo (meses)", min_value=1, max_value=120,
                                    value=12, step=1, key="diy_novo_prazo")

        if st.button("Adicionar Produto", use_container_width=True, key="btn_add_produto"):
            if nome and nome.strip():
                novo = Produto(
                    nome=nome.strip(),
                    tipo=TipoProduto(tipo),
                    taxa_cdi=taxa,
                    valor=valor,
                    prazo_meses=prazo,
                )
                diy.produtos.append(novo)
                cenario.carteira_diy = diy
                salvar_cenario(cenario)
                st.rerun()
            else:
                st.warning("Digite um nome para o produto.")

    # Exibir produtos existentes
    if diy.produtos:
        for i, p in enumerate(diy.produtos):
            col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 2, 1])
            with col1:
                st.text(p.nome)
            with col2:
                ir_label = "🟢 Isento" if p.is_isento_ir() else "🔴 IR"
                st.text(f"{p.tipo.value} {ir_label}")
            with col3:
                st.text(f"{p.taxa_cdi:.0f}% CDI")
            with col4:
                st.text(f"R$ {p.valor:,.2f}")
            with col5:
                st.text(f"{p.prazo_meses}m")
            with col6:
                if st.button("🗑️", key=f"del_prod_{i}"):
                    diy.produtos.pop(i)
                    cenario.carteira_diy = diy
                    salvar_cenario(cenario)
                    st.rerun()

        # Totalizador
        total = sum(p.valor for p in diy.produtos)
        st.info(f"**Total alocado:** R$ {total:,.2f} | **Produtos:** {len(diy.produtos)}")

    return diy
