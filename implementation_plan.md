# Comparador de Carteiras — Administrada vs DIY

Aplicação web local (Python + Streamlit) para comparar o desempenho de uma Carteira Administrada de Renda Fixa contra uma Carteira DIY montada pelo usuário, com múltiplos cenários salvos.

## Entendimento Confirmado

### Carteira Administrada
- Rendimento líquido = **Target% × CDI** (padrão 97%, ajustável)
- Taxa de administração = **X% a.a. sobre patrimônio total** (padrão 1%, ajustável)
- IR = **zero**
- Rendimento bruto = líquido + taxa admin

### Carteira DIY
- N produtos (CDB ou LCI/LCA), cada um com: nome, tipo, taxa (% CDI), valor alocado, prazo (meses)
- **CDB:** IR pela tabela regressiva no vencimento. Reinveste líquido em produto idêntico
- **LCI/LCA:** Isento de IR. Reinveste bruto em produto idêntico
- Tabela IR: 22,5% (≤180d) → 20% (181-360d) → 17,5% (361-720d) → 15% (>720d)

### Parâmetros Globais
- CDI: projeção por ano (ex: Ano 1: 14%, Ano 2: 12%, Ano 3: 10%)
- Janela de investimento: configurável (padrão 36 meses)
- Valores investidos: independentes por carteira
- Granularidade: mensal

### Saídas
- Gráfico mensal de evolução patrimonial
- Comparação de múltiplos cenários no mesmo gráfico
- Resumo: lucro bruto, lucro líquido, IR pago, taxa admin paga

---

## Proposed Changes

### Arquitetura Modular (Recomendada)

Estrutura do projeto organizada em módulos para clareza e manutenibilidade:

```
simulador_investimentos/
├── app.py                  # Entrada principal Streamlit
├── requirements.txt        # Dependências
├── engine/
│   ├── __init__.py
│   ├── carteira_admin.py   # Motor de cálculo da carteira administrada
│   ├── carteira_diy.py     # Motor de cálculo da carteira DIY
│   ├── ir.py               # Tabela regressiva de IR
│   └── cdi.py              # Projeção CDI e cálculo mensal
├── models/
│   ├── __init__.py
│   └── cenario.py          # Dataclasses para cenário, produto, resultado
├── persistence/
│   ├── __init__.py
│   └── storage.py          # Load/save cenários em JSON
├── ui/
│   ├── __init__.py
│   ├── sidebar.py          # Sidebar: gerenciar cenários
│   ├── input_admin.py      # Form: carteira administrada
│   ├── input_diy.py        # Form: carteira DIY
│   ├── charts.py           # Gráficos Plotly
│   └── summary.py          # Tabelas de resumo
└── data/
    └── cenarios.json       # Dados persistidos
```

---

### Detalhes dos Módulos

#### [NEW] [requirements.txt](file:///c:/Users/lucas/OneDrive/Documentos/GitHub/simulador_investimentos/requirements.txt)
Dependências: `streamlit`, `plotly`, `pandas`

---

#### [NEW] [cenario.py](file:///c:/Users/lucas/OneDrive/Documentos/GitHub/simulador_investimentos/models/cenario.py)
Dataclasses Python para tipagem forte:
- `Produto`: nome, tipo (CDB/LCI/LCA), taxa_cdi (%), valor, prazo_meses
- `CarteiraAdmin`: valor_investido, target_pct, taxa_admin_pct
- `CarteiraDIY`: lista de Produto
- `ProjecaoCDI`: lista de (ano, taxa)
- `Cenario`: nome, janela_meses, projecao_cdi, carteira_admin, carteira_diy
- `ResultadoMensal`: mes, valor_admin, valor_diy
- `Resumo`: lucro_bruto, lucro_liquido, ir_pago, taxa_admin_paga

---

#### [NEW] [cdi.py](file:///c:/Users/lucas/OneDrive/Documentos/GitHub/simulador_investimentos/engine/cdi.py)
- `taxa_mensal_cdi(taxa_anual)` → converte taxa anual para mensal equivalente
- `get_taxa_cdi_mes(projecao, mes)` → retorna a taxa CDI para um mês específico baseado na projeção por ano

---

#### [NEW] [ir.py](file:///c:/Users/lucas/OneDrive/Documentos/GitHub/simulador_investimentos/engine/ir.py)
- `aliquota_ir(dias)` → retorna a alíquota baseada na tabela regressiva
- `calcular_ir(rendimento, dias)` → calcula o valor do IR

---

#### [NEW] [carteira_admin.py](file:///c:/Users/lucas/OneDrive/Documentos/GitHub/simulador_investimentos/engine/carteira_admin.py)
Simula mês a mês:
1. Calcula rendimento mensal = `patrimonio × taxa_mensal_cdi × target_pct`
2. Calcula taxa admin mensal = `patrimonio × (taxa_admin / 12)`
3. Patrimônio líquido cresce por rendimento líquido
4. Acumula: rendimento bruto (líquido + admin), taxa admin paga

Retorna: lista de `ResultadoMensal` + `Resumo`

---

#### [NEW] [carteira_diy.py](file:///c:/Users/lucas/OneDrive/Documentos/GitHub/simulador_investimentos/engine/carteira_diy.py)
Simula mês a mês para cada produto:
1. Para cada produto ativo, calcula rendimento mensal = `valor × taxa_mensal_cdi × taxa_produto_pct`
2. Se o mês = vencimento do produto:
   - CDB: calcula IR sobre rendimento acumulado do produto, reinveste líquido em produto idêntico (contagem IR recomeça)
   - LCI/LCA: reinveste bruto em produto idêntico
3. No mês final, liquida todos os produtos (CDB paga IR final)
4. Soma patrimônio de todos os produtos

Retorna: lista de `ResultadoMensal` + `Resumo`

---

#### [NEW] [storage.py](file:///c:/Users/lucas/OneDrive/Documentos/GitHub/simulador_investimentos/persistence/storage.py)
- `salvar_cenario(cenario)` → serializa para JSON e salva em `data/cenarios.json`
- `carregar_cenarios()` → carrega todos os cenários
- `deletar_cenario(nome)` → remove cenário por nome
- `listar_cenarios()` → retorna nomes dos cenários salvos

---

#### [NEW] [app.py](file:///c:/Users/lucas/OneDrive/Documentos/GitHub/simulador_investimentos/app.py)
Interface Streamlit com:

**Sidebar:**
- Seletor/criador de cenários (nome)
- Botões: Novo, Salvar, Deletar
- Seletor de cenários para comparação (multiselect)

**Página principal — 3 tabs:**

1. **Configuração:** Janela (meses), projeção CDI por ano, valor + parâmetros da carteira admin, lista de produtos DIY (tabela editável)
2. **Resultados:** Gráfico Plotly com evolução mensal (uma linha por carteira por cenário + tabela resumo com lucro bruto, líquido, IR, taxa admin)
3. **Comparação:** Gráfico sobrepondo múltiplos cenários selecionados

---

## Decision Log

| # | Decisão | Alternativas | Motivo |
|---|---------|--------------|--------|
| 1 | Target = % do CDI líquido | % do capital investido | Alinhado com como assessores apresentam propostas |
| 2 | CDI projetado por ano | CDI fixo; API automática | Flexibilidade sem dependência externa |
| 3 | Valores independentes por carteira | Valor único dividido | Mais liberdade para simular cenários reais |
| 4 | Reinvestimento em produto idêntico | Cadeia de reinvestimentos | YAGNI — simplicidade para v1 |
| 5 | IR pago no vencimento, contagem recomeça | IR acumulado continuo | Reflete a realidade fiscal brasileira |
| 6 | Streamlit + Plotly | Excel; Jupyter; Terminal | Melhor UX para ferramenta pessoal recorrente |
| 7 | JSON local | SQLite; PostgreSQL | Simplicidade, portabilidade, suficiente para uso pessoal |
| 8 | Arquitetura modular | App single-file | Melhor manutenibilidade com complexidade moderada |
| 9 | Carteira admin: IR zero, target líquido | Carteira admin com IR calculado | Reflete como a proposta é apresentada ao investidor |
| 10 | Múltiplos cenários comparáveis | Cenário único | Maior poder de análise |

---

## Verification Plan

### Testes Automatizados
Será criado um arquivo `tests/test_engine.py` com pytest:

```bash
cd c:\Users\lucas\OneDrive\Documentos\GitHub\simulador_investimentos
pip install pytest
python -m pytest tests/ -v
```

Testes cobrindo:
1. **`test_taxa_mensal_cdi`** — Conversão de CDI anual para mensal (ex: 14% a.a. → ~1.0979% a.m.)
2. **`test_aliquota_ir`** — Tabela regressiva retorna alíquotas corretas por faixa de dias
3. **`test_carteira_admin_simples`** — Com CDI 14%, target 97%, 36 meses, verifica que rendimento líquido ≈ 97% CDI
4. **`test_carteira_diy_cdb_sem_reinvestimento`** — CDB de 36 meses, verifica IR na alíquota de 15%
5. **`test_carteira_diy_lci_isenta`** — LCI de 36 meses, verifica IR = 0
6. **`test_carteira_diy_reinvestimento`** — CDB de 12 meses em janela de 36, verifica 3 ciclos de IR
7. **`test_persistencia`** — Salvar e carregar cenário, verificar igualdade

### Validação Manual no Navegador
1. Executar `streamlit run app.py`
2. Criar um cenário "Teste" com valores conhecidos
3. Verificar que o gráfico exibe as duas linhas (admin vs DIY)
4. Salvar, fechar, reabrir — verificar que o cenário persiste
5. Criar segundo cenário, selecionar ambos na comparação, verificar gráfico sobreposto
