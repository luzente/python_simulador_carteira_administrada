"""Persistência de cenários em JSON local."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from models.cenario import (
    CarteiraAdmin,
    CarteiraDIY,
    Cenario,
    Produto,
    ProjecaoCDI,
    TipoProduto,
)

# Caminho padrão para o arquivo de dados
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_FILE = DATA_DIR / "cenarios.json"


def _cenario_to_dict(cenario: Cenario) -> dict:
    """Serializa um cenário para dicionário."""
    return {
        "nome": cenario.nome,
        "janela_meses": cenario.janela_meses,
        "projecao_cdi": {
            "taxas_anuais": cenario.projecao_cdi.taxas_anuais,
        },
        "carteira_admin": {
            "valor_investido": cenario.carteira_admin.valor_investido,
            "target_pct": cenario.carteira_admin.target_pct,
            "taxa_admin_pct": cenario.carteira_admin.taxa_admin_pct,
        },
        "carteira_diy": {
            "produtos": [
                {
                    "nome": p.nome,
                    "tipo": p.tipo.value,
                    "taxa_cdi": p.taxa_cdi,
                    "valor": p.valor,
                    "prazo_meses": p.prazo_meses,
                }
                for p in cenario.carteira_diy.produtos
            ]
        },
    }


def _dict_to_cenario(data: dict) -> Cenario:
    """Deserializa um dicionário para cenário."""
    produtos = [
        Produto(
            nome=p["nome"],
            tipo=TipoProduto(p["tipo"]),
            taxa_cdi=p["taxa_cdi"],
            valor=p["valor"],
            prazo_meses=p["prazo_meses"],
        )
        for p in data.get("carteira_diy", {}).get("produtos", [])
    ]

    admin_data = data.get("carteira_admin", {})
    cdi_data = data.get("projecao_cdi", {})

    return Cenario(
        nome=data["nome"],
        janela_meses=data.get("janela_meses", 36),
        projecao_cdi=ProjecaoCDI(
            taxas_anuais=cdi_data.get("taxas_anuais", [14.0]),
        ),
        carteira_admin=CarteiraAdmin(
            valor_investido=admin_data.get("valor_investido", 100000.0),
            target_pct=admin_data.get("target_pct", 97.0),
            taxa_admin_pct=admin_data.get("taxa_admin_pct", 1.0),
        ),
        carteira_diy=CarteiraDIY(produtos=produtos),
    )


def _ensure_data_dir():
    """Cria o diretório de dados se não existir."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_all() -> Dict[str, dict]:
    """Carrega todos os cenários do arquivo JSON."""
    if not DATA_FILE.exists():
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {item["nome"]: item for item in data}
    except (json.JSONDecodeError, KeyError):
        return {}


def _save_all(cenarios: Dict[str, dict]):
    """Salva todos os cenários no arquivo JSON."""
    _ensure_data_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(list(cenarios.values()), f, ensure_ascii=False, indent=2)


def listar_cenarios() -> List[str]:
    """Retorna nomes de todos os cenários salvos."""
    return list(_load_all().keys())


def carregar_cenario(nome: str) -> Optional[Cenario]:
    """Carrega um cenário específico pelo nome."""
    cenarios = _load_all()
    if nome in cenarios:
        return _dict_to_cenario(cenarios[nome])
    return None


def carregar_todos_cenarios() -> List[Cenario]:
    """Carrega todos os cenários salvos."""
    cenarios = _load_all()
    return [_dict_to_cenario(data) for data in cenarios.values()]


def salvar_cenario(cenario: Cenario):
    """Salva ou atualiza um cenário (usa o nome como chave)."""
    cenarios = _load_all()
    cenarios[cenario.nome] = _cenario_to_dict(cenario)
    _save_all(cenarios)


def deletar_cenario(nome: str) -> bool:
    """Deleta um cenário pelo nome. Retorna True se existia."""
    cenarios = _load_all()
    if nome in cenarios:
        del cenarios[nome]
        _save_all(cenarios)
        return True
    return False
