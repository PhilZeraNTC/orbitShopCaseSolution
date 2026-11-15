# PRD — Case OrbitShop (Due Diligence Series C | Peers Consulting & Technology)

## 1. Objetivo e Entregável
Construir um repositório Python auto-contido, determinístico e auditável que reproduz integralmente a análise de Due Diligence da OrbitShop (Q1 a Q9), acompanhado de testes unitários (`pytest`), gráficos estáticos em alta resolução (300 DPI), Jupyter Notebook executado (`notebooks/analise_orbitshop.ipynb`), Memo Executivo de 1 página (`reports/memo_orbitshop.md` e `reports/memo_orbitshop.pdf`) e `README.md` executivo.

## 2. Arquitetura e Stack Obrigatória
## Referência de Implementação Existente (Brownfield)
- O arquivo `notebooks/01_eda_auditoria_exploratoria.ipynb` contém a investigação exploratória original validada pelo autor.
- Os agentes devem ler esse notebook para extrair, refatorar e modularizar as funções de carga, auditoria e métricas em `src/loader.py`, `src/audit.py` e `src/metrics.py`, preservando rigorosamente as mesmas regras de negócio e resultados numéricos.
- O notebook `notebooks/01_eda_auditoria_exploratoria.ipynb` deve ser preservado no repositório como histórico de auditoria; o entregável executivo limpo deve ser gerado em `notebooks/02_analise_executiva.ipynb` importando `src/`.
- **Gerenciamento de dependências:** `uv` (`pyproject.toml` + `uv.lock`) com `requirements.txt` espelhado para compatibilidade universal com `pip`.
- **Dependências enxutas:** `pandas`, `openpyxl`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `jupyter`, `nbconvert`, `pytest`, `ruff`. (Não usar `plotly`, `skimpy` ou `missingno` no pipeline final para garantir renderização nativa no GitHub e build rápido).
- **Automação:** `Makefile` com alvos `setup`, `test`, `reproduce` (executa testes + roda o notebook via `nbconvert --to notebook --execute --inplace`) e `all`.
- **Estrutura de diretórios:**
  - `data/Base_Dados_OrbitShop.xlsx` (base original intacta)
  - `src/__init__.py`
  - `src/loader.py`: carga tipada das 6 abas (`Clientes`, `Produtos`, `Pedidos`, `Itens_Pedido`, `Tickets_Suporte`, `Avaliacoes`) e auditoria de integridade relacional/temporal.
  - `src/audit.py`: auditoria de nulos, regras comerciais (`preco_praticado`, margem negativa, contradições de cupom) e reconciliação financeira Q6 (`Pedidos.valor_total` vs. `Itens_Pedido`).
  - `src/metrics.py`: funções puras e determinísticas para o paradoxo Camila vs. Rogério e questões Q2, Q3, Q4, Q5, Q7 e Q8.
  - `src/charts.py`: geração de gráficos estáticos PNG (300 DPI) em `reports/figures/` (status de pedidos, reconciliação B2B/B2C, cancelamento por canal de aquisição, série mensal 2023–2024 e qualidade/tickets por fornecedor).
  - `notebooks/analise_orbitshop.ipynb`: notebook narrativo limpo importando funções de `src/`, exibindo tabelas formatadas e gráficos inline (já executado e salvo com outputs).
  - `tests/test_metrics.py`: testes `pytest` validando as premissas de negócio e números-chave abaixo.
  - `reports/memo_orbitshop.md` e `reports/memo_orbitshop.pdf`: Memo de 1 página com no máximo 400 palavras.
  - `README.md`: guia de execução em 1 comando, resumo executivo, tabela de rastreabilidade Q1–Q9 e gráficos embutidos.

## 3. Regras de Negócio e Ground Truth Validado (Invariantes para Código e Testes)
1. **Integridade da Base:**
   - `Clientes`: 3.000 linhas (0 nulos); `Produtos`: 200 linhas (0 nulos); `Pedidos`: 15.000 linhas (`valor_total` com 79 nulos = 0,53%); `Itens_Pedido`: 36.740 linhas (`desconto_aplicado` com 301 nulos = 0,82%); `Tickets_Suporte`: 4.000 linhas (`data_resolucao` com 1.653 nulos = 41,33%); `Avaliacoes`: 8.000 linhas (`comentario` com 1.679 nulos = 20,99%).
   - Zero chaves duplicadas e zero chaves estrangeiras órfãs.
2. **Fonte da Verdade Financeira (Q6):**
   - `0` de `14.921` pedidos válidos conciliam (±R$ 0,05) entre `Pedidos.valor_total` (R$ 38.418.252,65) e a soma líquida de `Itens_Pedido` (R$ 165.878.066,67; diferença de -R$ 127.459.814,02).
   - **Decisão:** Usar `Pedidos.valor_total` como fonte oficial de receita/ticket (imputando os 79 nulos pela mediana do segmento: B2B = R$ 7.803,97; B2C = R$ 1.255,37), pois valida a premissa da CEO (B2B = 6,15x B2C: R$ 7.778,34 vs. R$ 1.264,72), enquanto `Itens_Pedido` possui distorção de ETL (tickets ~R$ 11 mil iguais entre B2B/B2C, correlação r = -0,01, 21.243 descontos sem cupom e 2.574 itens abaixo do custo). Usar `Itens_Pedido` apenas para volume físico e mix relativo por categoria/fornecedor.
3. **Paradoxo Growth vs. CFO e Q2 (Status):**
   - Cancelamento global: 16,91% (2.537/15.000) — 2023: 16,78% (1.407/8.386); 2024: 17,08% (1.130/6.614).
   - Distribuição Q2: `entregue` 9.959 (66,39%), `cancelado` 2.537 (16,91%), `em_transito` 1.371 (9,14% — sendo 788 pedidos de 2023), `devolvido` 1.133 (7,55%). Não convertidos (`cancelado` + `devolvido`) = 24,47% (3.670 pedidos / R$ 9,47M).
4. **Q3 (Categorias):**
   - Volume (unidades): 1º Eletrônicos (18.658), 2º Casa & Decoração (17.899), 3º Moda (15.680).
   - Receita relativa (`Itens_Pedido`): 1º Eletrônicos (R$ 30,80M), 2º Casa & Decoração (R$ 24,52M), 3º Beleza & Saúde (R$ 23,35M), 4º Esporte & Lazer (R$ 20,23M), 5º Moda (R$ 19,86M). Divergência explicada pelo menor preço médio praticado em Moda (R$ 1.347,98).
5. **Q4 (Canais de Aquisição):**
   - Taxa de cancelamento: `paid_search` = 30,74% (1.219/3.965) vs. `indicação` 12,38%, `orgânico` 11,78%, `redes_sociais` 11,67% ($\chi^2 = 734{,}42$, $p = 7{,}22 \times 10^{-159}$). Ticket médio uniforme (~R$ 2.521–2.657; `paid_search` = R$ 2.553,51).
6. **Q5 (Evolução Mensal):**
   - Média de 551 pedidos/mês fora nov/2023. Pico isolado em `2023-11` com 2.317 pedidos (4,2x a média), simétrico entre `site` (770), `app` (783) e `marketplace` (764). Em `2024-11` foram 585 pedidos.
7. **Q7 (Fornecedores e Suporte):**
   - `DeltaFornece ME` é outlier de qualidade (nota média 2,30 vs. 3,62–3,84; 59,90% notas 1–2), mas sua taxa de tickets/100 itens (22,94) é igual aos pares (22,16–24,85). O salto de chamados em nov/2023 (375) e dez/2023 (391) ocorreu simultaneamente nos 9 fornecedores por transbordamento do pico de pedidos da Black Friday 2023.
8. **Q8 (Recomendação Única):**
   - Reestruturar `paid_search` (pausar campanhas de baixa intenção e realocar verba para canais orgânicos/indicação). Reduzir cancelamento de 30,74% para 11,9% recupera ~747 pedidos e ~R$ 1,91M em receita bruta.