# OrbitShop Due Diligence Series C (Case Peers Consulting & Technology)

## What This Is

Um repositório Python auto-contido, determinístico e auditável que reproduz integralmente a análise de Due Diligence Series C da OrbitShop (questões Q1 a Q9), refatorando a investigação exploratória validada (`notebooks/01_eda_auditoria_exploratoria.ipynb`) em módulos testados (`src/loader.py`, `src/audit.py`, `src/metrics.py`, `src/charts.py`). Entrega suíte de testes unitários (`pytest`) validando os invariantes numéricos de Ground Truth, gráficos estáticos em alta resolução (300 DPI), Jupyter Notebook executivo executado (`notebooks/02_analise_executiva.ipynb` / `notebooks/analise_orbitshop.ipynb`), Memo Executivo de 1 página (`reports/memo_orbitshop.md` e `reports/memo_orbitshop.pdf`, máx. 400 palavras) e `README.md` executivo com execução automatizada via `Makefile`.

## Core Value

Reprodutibilidade determinística e auditável de 100% dos números-chave e invariantes de negócio da Due Diligence da OrbitShop (Q1 a Q9) a partir da base original `Base_Dados_OrbitShop.xlsx`, validada por testes automatizados (`pytest`) e executável em 1 comando (`make reproduce` / `make all`).

## Business Context

- **Customer**: Comitê de Investimentos (Due Diligence Series C) e avaliadores técnicos da Peers Consulting & Technology
- **Revenue model**: Decisão de alocação de capital Series C e recuperação de margem/receita (~R$ 1,91M em receita bruta recuperável via reestruturação de `paid_search`)
- **Success metric**: 100% dos invariantes numéricos Q1–Q9 validados via `pytest`, execução limpa ponta a ponta via `Makefile` e Memo Executivo <= 400 palavras
- **Strategy notes**: `PRD.md` e `notebooks/01_eda_auditoria_exploratoria.ipynb`

## Requirements

### Validated

- ✓ Investigação exploratória e definição de Ground Truth das 6 abas (`Clientes`, `Produtos`, `Pedidos`, `Itens_Pedido`, `Tickets_Suporte`, `Avaliacoes`) em `notebooks/01_eda_auditoria_exploratoria.ipynb` — existing
- ✓ Base de dados bruta `Base_Dados_OrbitShop.xlsx` presente no repositório — existing

### Active

- [ ] Ambiente e gerenciamento de dependências reproduzível com `uv` (`pyproject.toml` + `uv.lock`), `requirements.txt` espelhado e `Makefile` (`setup`, `test`, `reproduce`, `all`)
- [ ] Preservação de `notebooks/01_eda_auditoria_exploratoria.ipynb` e organização de `data/Base_Dados_OrbitShop.xlsx`
- [ ] Módulo `src/loader.py` com carga tipada das 6 abas e auditoria de integridade relacional/temporal (0 chaves duplicadas, 0 FKs órfãs)
- [ ] Módulo `src/audit.py` com auditoria de nulos, regras comerciais (`preco_praticado`, margem negativa, contradições de cupom) e reconciliação financeira Q6 (`Pedidos.valor_total` vs `Itens_Pedido`, imputação de 79 nulos pela mediana B2B/B2C)
- [ ] Módulo `src/metrics.py` com funções puras e determinísticas para o paradoxo Camila vs. Rogério e questões Q2, Q3, Q4, Q5, Q7 e Q8
- [ ] Suíte de testes `tests/test_metrics.py` (`pytest`) validando rigorosamente todos os invariantes e números-chave do Ground Truth (Q1–Q9)
- [ ] Módulo `src/charts.py` gerando gráficos estáticos PNG em 300 DPI em `reports/figures/` (status de pedidos, reconciliação B2B/B2C, cancelamento por canal de aquisição, série mensal 2023–2024 e qualidade/tickets por fornecedor)
- [ ] Notebook executivo limpo e executado (`notebooks/02_analise_executiva.ipynb` e `notebooks/analise_orbitshop.ipynb`) importando `src/`, com tabelas formatadas e gráficos inline
- [ ] Memo Executivo de 1 página (`reports/memo_orbitshop.md` e `reports/memo_orbitshop.pdf`) com no máximo 400 palavras
- [ ] `README.md` executivo com guia de execução em 1 comando, resumo executivo, tabela de rastreabilidade Q1–Q9 e gráficos embutidos

### Out of Scope

- Uso de `plotly`, `skimpy` ou `missingno` no pipeline final — excluídos para garantir renderização nativa no GitHub e build rápido
- Alteração ou limpeza destrutiva do arquivo bruto `Base_Dados_OrbitShop.xlsx` — a base original deve permanecer intacta para auditabilidade
- Remoção do notebook histórico `notebooks/01_eda_auditoria_exploratoria.ipynb` — deve ser preservado como registro da auditoria exploratória

## Context

- **Referência Brownfield**: O arquivo `notebooks/01_eda_auditoria_exploratoria.ipynb` contém toda a investigação exploratória original validada pelo autor. O código de produção em `src/` deve extrair, refatorar e modularizar as funções de carga, auditoria e métricas desse notebook preservando exatamente as mesmas regras de negócio e resultados numéricos.
- **Ground Truth Validado (Invariantes)**:
  1. **Integridade da Base**: `Clientes` (3.000 linhas, 0 nulos); `Produtos` (200 linhas, 0 nulos); `Pedidos` (15.000 linhas, `valor_total` com 79 nulos = 0,53%); `Itens_Pedido` (36.740 linhas, `desconto_aplicado` com 301 nulos = 0,82%); `Tickets_Suporte` (4.000 linhas, `data_resolucao` com 1.653 nulos = 41,33%); `Avaliacoes` (8.000 linhas, `comentario` com 1.679 nulos = 20,99%). Zero chaves duplicadas e zero chaves estrangeiras órfãs.
  2. **Fonte da Verdade Financeira (Q6)**: `0` de `14.921` pedidos válidos conciliam (±R$ 0,05) entre `Pedidos.valor_total` (R$ 38.418.252,65) e a soma líquida de `Itens_Pedido` (R$ 165.878.066,67; diferença de -R$ 127.459.814,02). `Pedidos.valor_total` é a fonte oficial de receita/ticket (imputando 79 nulos pela mediana do segmento: B2B = R$ 7.803,97; B2C = R$ 1.255,37), validando a premissa da CEO (B2B = 6,15x B2C: R$ 7.778,34 vs. R$ 1.264,72). `Itens_Pedido` apresenta distorção de ETL (tickets ~R$ 11 mil iguais entre B2B/B2C, correlação r = -0,01, 21.243 descontos sem cupom e 2.574 itens abaixo do custo) e deve ser usado apenas para volume físico e mix relativo por categoria/fornecedor.
  3. **Paradoxo Growth vs. CFO e Q2 (Status)**: Cancelamento global 16,91% (2.537/15.000) — 2023: 16,78% (1.407/8.386); 2024: 17,08% (1.130/6.614). Distribuição Q2: `entregue` 9.959 (66,39%), `cancelado` 2.537 (16,91%), `em_transito` 1.371 (9,14% — sendo 788 de 2023), `devolvido` 1.133 (7,55%). Não convertidos (`cancelado` + `devolvido`) = 24,47% (3.670 pedidos / R$ 9,47M).
  4. **Q3 (Categorias)**: Volume (unidades): 1º Eletrônicos (18.658), 2º Casa & Decoração (17.899), 3º Moda (15.680). Receita relativa (`Itens_Pedido`): 1º Eletrônicos (R$ 30,80M), 2º Casa & Decoração (R$ 24,52M), 3º Beleza & Saúde (R$ 23,35M), 4º Esporte & Lazer (R$ 20,23M), 5º Moda (R$ 19,86M). Menor preço médio praticado em Moda (R$ 1.347,98).
  5. **Q4 (Canais de Aquisição)**: Taxa de cancelamento: `paid_search` = 30,74% (1.219/3.965) vs. `indicação` 12,38%, `orgânico` 11,78%, `redes_sociais` 11,67% (chi2 = 734,42, p = 7,22e-159). Ticket médio uniforme (~R$ 2.521–2.657; `paid_search` = R$ 2.553,51).
  6. **Q5 (Evolução Mensal)**: Média de 551 pedidos/mês fora nov/2023. Pico isolado em `2023-11` com 2.317 pedidos (4,2x a média), simétrico entre `site` (770), `app` (783) e `marketplace` (764). Em `2024-11` foram 585 pedidos.
  7. **Q7 (Fornecedores e Suporte)**: `DeltaFornece ME` é outlier de qualidade (nota média 2,30 vs. 3,62–3,84; 59,90% notas 1–2), mas sua taxa de tickets/100 itens (22,94) é igual aos pares (22,16–24,85). Salto de chamados em nov/2023 (375) e dez/2023 (391) ocorreu simultaneamente nos 9 fornecedores por transbordamento da Black Friday 2023.
  8. **Q8 (Recomendação Única)**: Reestruturar `paid_search` (pausar campanhas de baixa intenção e realocar verba para canais orgânicos/indicação). Reduzir cancelamento de 30,74% para 11,9% recupera ~747 pedidos e ~R$ 1,91M em receita bruta.

## Constraints

- **Tech Stack**: Python com `uv` (`pyproject.toml` + `uv.lock`) e `requirements.txt` espelhado — garante reprodutibilidade moderna e compatibilidade universal com `pip`
- **Dependencies**: Apenas `pandas`, `openpyxl`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `jupyter`, `nbconvert`, `pytest`, `ruff` (mais ferramenta leve para geração do PDF do memo se necessário) — sem `plotly`, `skimpy` ou `missingno`
- **Determinismo Numérico**: Funções em `src/` devem reproduzir exatamente os valores validados no Ground Truth e em `notebooks/01_eda_auditoria_exploratoria.ipynb`
- **Qualidade Visual**: Gráficos estáticos exportados em PNG a 300 DPI em `reports/figures/`
- **Restrição Editorial**: Memo executivo (`reports/memo_orbitshop.md` e `reports/memo_orbitshop.pdf`) deve ter 1 página e no máximo 400 palavras
- **Estrutura de Fases**: Divisão em 2 fases conforme definido pelo usuário: Fase 1 (Core & Testes) e Fase 2 (Notebook & Gráficos & Entregáveis Executivos)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Usar `Pedidos.valor_total` como fonte oficial de receita/ticket (imputando 79 nulos pela mediana B2B/B2C) | Valida premissa da CEO (B2B = 6,15x B2C) e isola distorção de ETL em `Itens_Pedido` | ✓ Good |
| Usar `Itens_Pedido` apenas para volume físico e mix relativo por categoria/fornecedor | Contém granularidade de produto/categoria/fornecedor não existente no cabeçalho `Pedidos` | ✓ Good |
| Extrair e modularizar lógica de `01_eda_auditoria_exploratoria.ipynb` para `src/` | Garante paridade 100% com a análise exploratória já auditada e permite testes unitários com `pytest` | — Pending |
| Estruturar roadmap em 2 fases: Fase 1 (Core & Testes) e Fase 2 (Notebook & Gráficos) | Diretriz explícita do usuário na configuração do projeto | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-11-15 after initialization*
