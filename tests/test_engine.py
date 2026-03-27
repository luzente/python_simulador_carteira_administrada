"""Testes do motor de cálculo do simulador de investimentos."""

import sys
import os
import json
import tempfile
from pathlib import Path

# Adiciona raiz do projeto ao path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import pytest
from engine.cdi import taxa_anual_para_mensal, get_taxa_cdi_anual, get_taxa_cdi_mensal
from engine.ir import aliquota_ir, calcular_ir, meses_para_dias
from engine.carteira_admin import simular_carteira_admin
from engine.carteira_diy import simular_carteira_diy
from models.cenario import (
    CarteiraAdmin,
    CarteiraDIY,
    Cenario,
    Produto,
    ProjecaoCDI,
    TipoProduto,
)
from persistence.storage import (
    _cenario_to_dict,
    _dict_to_cenario,
)


# =============================================
# Testes CDI
# =============================================

class TestCDI:

    def test_taxa_anual_para_mensal_14pct(self):
        """14% a.a. ≈ 1.0979% a.m."""
        mensal = taxa_anual_para_mensal(14.0)
        assert abs(mensal - 1.0979) < 0.001

    def test_taxa_anual_para_mensal_zero(self):
        assert taxa_anual_para_mensal(0.0) == 0.0

    def test_taxa_anual_para_mensal_roundtrip(self):
        """12 meses acumulados devem dar a taxa anual original."""
        taxa_anual = 14.0
        taxa_mensal = taxa_anual_para_mensal(taxa_anual) / 100.0
        acumulado = (1 + taxa_mensal) ** 12 - 1
        assert abs(acumulado * 100 - taxa_anual) < 0.0001

    def test_get_taxa_cdi_anual_dentro_projecao(self):
        taxas = [14.0, 12.0, 10.0]
        assert get_taxa_cdi_anual(taxas, 1) == 14.0   # Mês 1  → Ano 1
        assert get_taxa_cdi_anual(taxas, 12) == 14.0  # Mês 12 → Ano 1
        assert get_taxa_cdi_anual(taxas, 13) == 12.0  # Mês 13 → Ano 2
        assert get_taxa_cdi_anual(taxas, 24) == 12.0  # Mês 24 → Ano 2
        assert get_taxa_cdi_anual(taxas, 25) == 10.0  # Mês 25 → Ano 3
        assert get_taxa_cdi_anual(taxas, 36) == 10.0  # Mês 36 → Ano 3

    def test_get_taxa_cdi_anual_alem_projecao(self):
        """Meses além da projeção usam a última taxa."""
        taxas = [14.0, 12.0]
        assert get_taxa_cdi_anual(taxas, 25) == 12.0  # Ano 3 → usa ano 2

    def test_get_taxa_cdi_anual_lista_vazia(self):
        assert get_taxa_cdi_anual([], 1) == 0.0


# =============================================
# Testes IR
# =============================================

class TestIR:

    def test_aliquota_ate_180_dias(self):
        assert aliquota_ir(1) == 22.5
        assert aliquota_ir(180) == 22.5

    def test_aliquota_181_a_360_dias(self):
        assert aliquota_ir(181) == 20.0
        assert aliquota_ir(360) == 20.0

    def test_aliquota_361_a_720_dias(self):
        assert aliquota_ir(361) == 17.5
        assert aliquota_ir(720) == 17.5

    def test_aliquota_acima_720_dias(self):
        assert aliquota_ir(721) == 15.0
        assert aliquota_ir(1000) == 15.0

    def test_calcular_ir_positivo(self):
        ir = calcular_ir(1000.0, 365)  # 17.5%
        assert abs(ir - 175.0) < 0.01

    def test_calcular_ir_rendimento_zero(self):
        assert calcular_ir(0.0, 365) == 0.0

    def test_calcular_ir_rendimento_negativo(self):
        assert calcular_ir(-100.0, 365) == 0.0

    def test_meses_para_dias(self):
        assert meses_para_dias(6) == 180
        assert meses_para_dias(12) == 360
        assert meses_para_dias(24) == 720


# =============================================
# Testes Carteira Administrada
# =============================================

class TestCarteiraAdmin:

    def test_simulacao_basica(self):
        """Simula 36 meses com CDI 14%, target 97%, taxa admin 1%."""
        admin = CarteiraAdmin(valor_investido=100000.0, target_pct=97.0, taxa_admin_pct=1.0)
        cdi = ProjecaoCDI(taxas_anuais=[14.0, 14.0, 14.0])

        evolucao, resumo = simular_carteira_admin(admin, cdi, 36)

        # Deve ter 36 pontos
        assert len(evolucao) == 36

        # Patrimônio deve crescer monotonicamente
        for i in range(1, len(evolucao)):
            assert evolucao[i] > evolucao[i - 1]

        # Resumo
        assert resumo.valor_inicial == 100000.0
        assert resumo.valor_final > 100000.0
        assert resumo.ir_pago == 0.0
        assert resumo.taxa_admin_paga > 0.0
        assert resumo.lucro_liquido > 0.0
        # Lucro bruto = líquido + taxa admin
        assert abs(resumo.lucro_bruto - (resumo.lucro_liquido + resumo.taxa_admin_paga)) < 0.01

    def test_target_100pct(self):
        """100% CDI deve render mais que 97% CDI."""
        cdi = ProjecaoCDI(taxas_anuais=[14.0])

        admin_97 = CarteiraAdmin(valor_investido=100000.0, target_pct=97.0, taxa_admin_pct=1.0)
        admin_100 = CarteiraAdmin(valor_investido=100000.0, target_pct=100.0, taxa_admin_pct=1.0)

        _, r97 = simular_carteira_admin(admin_97, cdi, 12)
        _, r100 = simular_carteira_admin(admin_100, cdi, 12)

        assert r100.lucro_liquido > r97.lucro_liquido

    def test_taxa_admin_zero(self):
        """Sem taxa admin, lucro bruto = lucro líquido."""
        admin = CarteiraAdmin(valor_investido=100000.0, target_pct=100.0, taxa_admin_pct=0.0)
        cdi = ProjecaoCDI(taxas_anuais=[14.0])

        _, resumo = simular_carteira_admin(admin, cdi, 12)

        assert resumo.taxa_admin_paga == 0.0
        assert abs(resumo.lucro_bruto - resumo.lucro_liquido) < 0.01


# =============================================
# Testes Carteira DIY
# =============================================

class TestCarteiraDIY:

    def test_cdb_36_meses_ir_15pct(self):
        """CDB de 36 meses (>720 dias) = IR de 15% no final."""
        produto = Produto("CDB X", TipoProduto.CDB, 100.0, 100000.0, 36)
        diy = CarteiraDIY(produtos=[produto])
        cdi = ProjecaoCDI(taxas_anuais=[14.0, 14.0, 14.0])

        _, resumo = simular_carteira_diy(diy, cdi, 36)

        assert resumo.ir_pago > 0.0
        # Com 36 meses (1080 dias), alíquota = 15%
        assert resumo.valor_final > 100000.0
        assert resumo.lucro_liquido > 0.0

    def test_lci_isenta_ir(self):
        """LCI não paga IR."""
        produto = Produto("LCI Y", TipoProduto.LCI, 90.0, 100000.0, 12)
        diy = CarteiraDIY(produtos=[produto])
        cdi = ProjecaoCDI(taxas_anuais=[14.0, 14.0, 14.0])

        _, resumo = simular_carteira_diy(diy, cdi, 12)

        assert resumo.ir_pago == 0.0
        assert resumo.lucro_liquido > 0.0

    def test_lca_isenta_ir(self):
        """LCA também não paga IR."""
        produto = Produto("LCA Z", TipoProduto.LCA, 90.0, 100000.0, 24)
        diy = CarteiraDIY(produtos=[produto])
        cdi = ProjecaoCDI(taxas_anuais=[14.0, 14.0])

        _, resumo = simular_carteira_diy(diy, cdi, 24)

        assert resumo.ir_pago == 0.0

    def test_reinvestimento_cdb_12m_em_36m(self):
        """CDB de 12 meses em janela de 36 → 3 ciclos, cada um com IR."""
        produto = Produto("CDB curto", TipoProduto.CDB, 110.0, 100000.0, 12)
        diy = CarteiraDIY(produtos=[produto])
        cdi = ProjecaoCDI(taxas_anuais=[14.0, 14.0, 14.0])

        _, resumo = simular_carteira_diy(diy, cdi, 36)

        # IR deve ser pago em 3 momentos (mês 12, 24, 36)
        assert resumo.ir_pago > 0.0
        # Evolução deve ter 36 pontos
        assert resumo.valor_final > 100000.0

    def test_cdb_12m_paga_mais_ir_que_36m(self):
        """CDB curto (12m, IR 20%) paga mais IR que longo (36m, IR 15%)."""
        p_curto = Produto("Curto", TipoProduto.CDB, 100.0, 100000.0, 12)
        p_longo = Produto("Longo", TipoProduto.CDB, 100.0, 100000.0, 36)
        cdi = ProjecaoCDI(taxas_anuais=[14.0, 14.0, 14.0])

        _, r_curto = simular_carteira_diy(CarteiraDIY([p_curto]), cdi, 36)
        _, r_longo = simular_carteira_diy(CarteiraDIY([p_longo]), cdi, 36)

        # CDB curto paga mais IR (20% × 3 ciclos vs 15% × 1 ciclo)
        assert r_curto.ir_pago > r_longo.ir_pago

    def test_carteira_vazia(self):
        """Carteira sem produtos retorna zeros."""
        diy = CarteiraDIY(produtos=[])
        cdi = ProjecaoCDI(taxas_anuais=[14.0])

        evolucao, resumo = simular_carteira_diy(diy, cdi, 12)

        assert len(evolucao) == 12
        assert all(v == 0.0 for v in evolucao)
        assert resumo.valor_final == 0.0

    def test_multiplos_produtos(self):
        """Carteira com CDB + LCI soma valores corretamente."""
        produtos = [
            Produto("CDB A", TipoProduto.CDB, 110.0, 50000.0, 12),
            Produto("LCI B", TipoProduto.LCI, 90.0, 50000.0, 12),
        ]
        diy = CarteiraDIY(produtos=produtos)
        cdi = ProjecaoCDI(taxas_anuais=[14.0])

        _, resumo = simular_carteira_diy(diy, cdi, 12)

        assert resumo.valor_inicial == 100000.0
        assert resumo.valor_final > 100000.0
        assert resumo.ir_pago > 0.0  # CDB paga IR


# =============================================
# Testes Persistência (serialização)
# =============================================

class TestPersistencia:

    def test_serialize_deserialize(self):
        """Cenário sobrevive ao ciclo de serialização."""
        cenario = Cenario(
            nome="Teste Full",
            janela_meses=24,
            projecao_cdi=ProjecaoCDI(taxas_anuais=[14.0, 12.0]),
            carteira_admin=CarteiraAdmin(
                valor_investido=200000.0,
                target_pct=95.0,
                taxa_admin_pct=0.8,
            ),
            carteira_diy=CarteiraDIY(produtos=[
                Produto("CDB X", TipoProduto.CDB, 110.0, 80000.0, 12),
                Produto("LCI Y", TipoProduto.LCI, 92.0, 120000.0, 24),
            ]),
        )

        # Serializa e deserializa
        data = _cenario_to_dict(cenario)
        recuperado = _dict_to_cenario(data)

        # Verifica igualdade
        assert recuperado.nome == cenario.nome
        assert recuperado.janela_meses == cenario.janela_meses
        assert recuperado.projecao_cdi.taxas_anuais == cenario.projecao_cdi.taxas_anuais
        assert recuperado.carteira_admin.valor_investido == cenario.carteira_admin.valor_investido
        assert recuperado.carteira_admin.target_pct == cenario.carteira_admin.target_pct
        assert recuperado.carteira_admin.taxa_admin_pct == cenario.carteira_admin.taxa_admin_pct
        assert len(recuperado.carteira_diy.produtos) == 2
        assert recuperado.carteira_diy.produtos[0].nome == "CDB X"
        assert recuperado.carteira_diy.produtos[0].tipo == TipoProduto.CDB
        assert recuperado.carteira_diy.produtos[1].nome == "LCI Y"
        assert recuperado.carteira_diy.produtos[1].tipo == TipoProduto.LCI

    def test_json_roundtrip(self):
        """Dados sobrevivem ao JSON encode/decode."""
        cenario = Cenario(
            nome="JSON Test",
            projecao_cdi=ProjecaoCDI(taxas_anuais=[14.0]),
            carteira_admin=CarteiraAdmin(valor_investido=100000.0),
            carteira_diy=CarteiraDIY(produtos=[
                Produto("CDB A", TipoProduto.CDB, 100.0, 50000.0, 6),
            ]),
        )

        data = _cenario_to_dict(cenario)
        json_str = json.dumps(data, ensure_ascii=False)
        data_back = json.loads(json_str)
        recuperado = _dict_to_cenario(data_back)

        assert recuperado.nome == "JSON Test"
        assert len(recuperado.carteira_diy.produtos) == 1
