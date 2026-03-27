# Simulador de Investimentos — Walkthrough

## O que foi construído

Aplicação Streamlit completa para comparar **Carteira Administrada** vs **Carteira DIY de Renda Fixa**, com motor de cálculo fiel ao mercado brasileiro (CDI variável, IR regressivo, LCI/LCA isentos).

## Estrutura do Projeto

```
simulador_investimentos/
├── app.py                    # Entry point Streamlit
├── engine/                   # Motores de cálculo
│   ├── cdi.py                # Projeção CDI (anual→mensal)
│   ├── ir.py                 # IR regressivo (22.5%→15%)
│   ├── carteira_admin.py     # Simulação carteira administrada
│   └── carteira_diy.py       # Simulação CDB/LCI/LCA com reinvestimento
├── models/cenario.py         # Dataclasses do domínio
├── persistence/storage.py    # Serialização JSON
├── ui/                       # Módulos de interface
│   ├── sidebar.py, input_admin.py, input_diy.py
│   ├── charts.py, summary.py
├── tests/test_engine.py      # 26 testes unitários
└── requirements.txt
```

## Testes

**26/26 testes passando** cobrindo:
- Conversão CDI anual↔mensal
- Alíquotas IR por faixa temporal
- Simulação carteira administrada (target + taxa admin)
- Simulação DIY (CDB com IR, LCI/LCA isentos, reinvestimento)
- Serialização/deserialização JSON

## Verificação no Navegador

````carousel
![Página inicial com sidebar para criação de cenários](C:\Users\lucas\.gemini\antigravity\brain\27876a80-443a-4848-8fcb-167e30b813de\initial_page_1774571503954.png)
<!-- slide -->
![Cenário criado com configuração de parâmetros globais, carteira administrada e DIY](C:\Users\lucas\.gemini\antigravity\brain\27876a80-443a-4848-8fcb-167e30b813de\scenario_created_1774571521427.png)
<!-- slide -->
![Aba Resultados com gráfico e tabela de resumo financeiro](C:\Users\lucas\.gemini\antigravity\brain\27876a80-443a-4848-8fcb-167e30b813de\results_tab_1774571531434.png)
````

## Como executar

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```
