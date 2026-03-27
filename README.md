## 📈 Simulador de Investimentos — Administrada vs. DIY
Este projeto é uma aplicação Streamlit robusta desenvolvida para comparar o desempenho financeiro entre uma Carteira Administrada de Renda Fixa e uma Carteira DIY (Do It Yourself). O motor de cálculo é fiel às particularidades do mercado brasileiro, incluindo projeções de CDI variável, tabelas regressivas de IR e isenções para LCI/LCA.

## 🛠️ Tecnologias e Arquitetura
O sistema utiliza uma estrutura modular para garantir manutenibilidade e precisão nos cálculos:

Linguagem: Python 3.9+.

Interface: Streamlit para o dashboard e Plotly para visualização de dados.

Engine: Módulos dedicados para cálculo de IR (regressivo), projeção de CDI e simulação de reinvestimentos automáticos.


Persistência: Armazenamento local em JSON para salvar e carregar diferentes cenários de investimento.

## 🚀 Instalação e Configuração
Siga os passos abaixo para configurar o ambiente e executar a aplicação em sua máquina local.

1. Criar Ambiente Virtual (venv)
Recomenda-se o uso do Python 3.10 ou superior. No terminal, dentro da pasta do projeto, execute:

``` Bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
``` 
2. Instalar Dependências
Com o ambiente virtual ativado, instale os pacotes necessários:


``` Bash
pip install -r requirements.txt
``` 
3. Executar o Simulador
Inicie o servidor do Streamlit:


``` Bash
python -m streamlit run app.py
``` 
4. Acessar no Navegador
Após o comando acima, o Streamlit abrirá automaticamente uma aba no seu navegador padrão. Caso não abra, acesse manualmente o endereço:
http://localhost:8501


## 📖 Como Usar o Simulador
A aplicação está dividida em três áreas principais para facilitar o seu fluxo de análise:

### A. Gerenciamento de Cenários (Sidebar)
Criar/Carregar: Dê um nome ao seu cenário e salve-o para consultas futuras.

Comparação Multi-Cenário: Selecione múltiplos cenários salvos para visualizar a sobreposição de resultados no gráfico comparativo.

### B. Configuração (Tab 1)
Nesta aba, você define as premissas do investimento:

Parâmetros Globais: Defina a janela de tempo (ex: 36 meses) e a projeção do CDI anual para cada ano do período.

Carteira Administrada: Insira o valor investido, o Target (% do CDI líquido) e a Taxa de Administração anual.

Carteira DIY: Adicione produtos individualmente (CDB, LCI ou LCA). Informe a taxa (% do CDI), o valor alocado e o prazo de vencimento de cada título.

### C. Resultados e Comparação (Tabs 2 e 3)

Evolução Mensal: Visualize o crescimento do patrimônio líquido mês a mês através de gráficos interativos do Plotly.

Resumo Financeiro: Analise a tabela comparativa que detalha o Lucro Bruto, Lucro Líquido, total de IR pago (na carteira DIY) e Taxas de Administração (na carteira Administrada).

## 🧪 Verificação Técnica
Para garantir que os cálculos de IR e CDI permaneçam precisos após qualquer alteração no código, você pode executar a suíte de testes unitários:

``` Bash
python -m pytest tests/test_engine.py -v
``` 
Nota: O simulador considera o reinvestimento automático do valor líquido (pós-IR) em produtos de mesmas características ao fim de cada vencimento na carteira DIY.
