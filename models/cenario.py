"""Modelos de dados para o simulador de investimentos."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class TipoProduto(str, Enum):
    """Tipo de produto de renda fixa."""
    CDB = "CDB"
    LCI = "LCI"
    LCA = "LCA"


@dataclass
class Produto:
    """Um produto de renda fixa na carteira DIY."""
    nome: str
    tipo: TipoProduto
    taxa_cdi: float          # % do CDI (ex: 110 = 110% do CDI)
    valor: float             # Valor alocado em R$
    prazo_meses: int         # Prazo até vencimento em meses

    def is_isento_ir(self) -> bool:
        """LCI e LCA são isentos de IR."""
        return self.tipo in (TipoProduto.LCI, TipoProduto.LCA)


@dataclass
class CarteiraAdmin:
    """Parâmetros da carteira administrada."""
    valor_investido: float   # Valor investido em R$
    target_pct: float = 97.0  # Target em % do CDI líquido (ex: 97)
    taxa_admin_pct: float = 1.0  # Taxa de administração % a.a. (ex: 1)


@dataclass
class CarteiraDIY:
    """Carteira montada pelo investidor."""
    produtos: List[Produto] = field(default_factory=list)

    @property
    def valor_total(self) -> float:
        """Valor total alocado na carteira DIY."""
        return sum(p.valor for p in self.produtos)


@dataclass
class ProjecaoCDI:
    """Projeção de CDI por ano."""
    taxas_anuais: List[float] = field(default_factory=list)
    # Índice 0 = Ano 1, Índice 1 = Ano 2, etc. Valores em % (ex: 14.0)


@dataclass
class Cenario:
    """Um cenário completo de simulação."""
    nome: str
    janela_meses: int = 36
    projecao_cdi: ProjecaoCDI = field(default_factory=ProjecaoCDI)
    carteira_admin: CarteiraAdmin = field(default_factory=lambda: CarteiraAdmin(valor_investido=100000.0))
    carteira_diy: CarteiraDIY = field(default_factory=CarteiraDIY)


@dataclass
class ResultadoMensal:
    """Resultado de um mês da simulação."""
    mes: int
    valor_admin: float
    valor_diy: float


@dataclass
class ResumoCarteira:
    """Resumo financeiro de uma carteira."""
    valor_inicial: float
    valor_final: float
    lucro_bruto: float
    lucro_liquido: float
    ir_pago: float
    taxa_admin_paga: float

    @property
    def rentabilidade_liquida_pct(self) -> float:
        """Rentabilidade líquida percentual."""
        if self.valor_inicial == 0:
            return 0.0
        return (self.lucro_liquido / self.valor_inicial) * 100


@dataclass
class ResultadoSimulacao:
    """Resultado completo de uma simulação."""
    cenario_nome: str
    evolucao_mensal: List[ResultadoMensal] = field(default_factory=list)
    resumo_admin: ResumoCarteira = None
    resumo_diy: ResumoCarteira = None
