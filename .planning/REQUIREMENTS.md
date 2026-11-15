# Requirements: OrbitShop Due Diligence Series C

**Defined:** 2026-11-15
**Core Value:** Reprodutibilidade determinística e auditável de 100% dos números-chave e invariantes de negócio da Due Diligence da OrbitShop (Q1 a Q9) a partir da base original `Base_Dados_OrbitShop.xlsx`, validada por testes automatizados (`pytest`) e executável em 1 comando (`make reproduce` / `make all`).

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Environment & Data Foundation (ENV)

- [x] **ENV-01**: Repositório configurado com `uv` (`pyproject.toml` + `uv.lock`) e `requirements.txt` espelhado contendo apenas as dependências enxutas (`pandas`, `openpyxl`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `jupyter`, `nbconvert`, `pytest`, `ruff`)
- [x] **ENV-02**: Base bruta disponível em `data/Base_Dados_OrbitShop.xlsx` intacta (100% idêntica em checksum ao arquivo original) e notebook histórico `notebooks/01_eda_auditoria_exploratoria.ipynb` preservado
- [x] **ENV-03**: `Makefile` com alvos funcionais `setup`, `test`, `reproduce` (testes + execução inplace do notebook via `nbconvert`) e `all`

### Data Loading & Relational Integrity (LOAD)

- [x] **LOAD-01**: `src/loader.py` carrega de forma tipada as 6 abas de `data/Base_Dados_OrbitShop.xlsx` (`Clientes`: 3.000 linhas, `Produtos`: 200 linhas, `Pedidos`: 15.000 linhas, `Itens_Pedido`: 36.740 linhas, `Tickets_Suporte`: 4.000 linhas, `Avaliacoes`: 8.000 linhas)
- [x] **LOAD-02**: `src/loader.py` audita integridade relacional e temporal comprovando zero chaves primárias duplicadas e zero chaves estrangeiras órfãs entre as 6 tabelas

### Data Audit & Financial Reconciliation (AUDT)

- [ ] **AUDT-01**: `src/audit.py` contabiliza exatamente os nulos das 6 abas (`Clientes`: 0, `Produtos`: 0, `Pedidos.valor_total`: 79 nulos / 0,53%, `Itens_Pedido.desconto_aplicado`: 301 nulos / 0,82%, `Tickets_Suporte.data_resolucao`: 1.653 nulos / 41,33%, `Avaliacoes.comentario`: 1.679 nulos / 20,99%)
- [ ] **AUDT-02**: `src/audit.py` audita anomalias comerciais em `Itens_Pedido`, identificando 21.243 itens com desconto sem cupom no pedido e 2.574 itens vendidos abaixo do `custo_unitario`
- [ ] **AUDT-03**: `src/audit.py` executa a reconciliação financeira Q6 demonstrando que 0 de 14.921 pedidos válidos conciliam (±R$ 0,05) entre `Pedidos.valor_total` (R$ 38.418.252,65) e a soma líquida de `Itens_Pedido` (R$ 165.878.066,67; diferença de -R$ 127.459.814,02, correlação r = -0,01)
- [ ] **AUDT-04**: `src/audit.py` imputa os 79 nulos de `Pedidos.valor_total` pela mediana do segmento (`B2B` = R$ 7.803,97; `B2C` = R$ 1.255,37) e valida a premissa da CEO de ticket médio B2B = 6,15x B2C (R$ 7.778,34 vs. R$ 1.264,72)

### Business Metrics Q1–Q8 (METR)

- [ ] **METR-01**: `src/metrics.py` resolve o paradoxo Growth (Camila) vs. CFO (Rogério) e a questão Q2, calculando cancelamento global de 16,91% (2.537/15.000; 2023: 16,78% = 1.407/8.386; 2024: 17,08% = 1.130/6.614), distribuição de status (`entregue` 9.959 / 66,39%, `cancelado` 2.537 / 16,91%, `em_transito` 1.371 / 9,14% com 788 de 2023, `devolvido` 1.133 / 7,55%) e volume não convertido (`cancelado` + `devolvido` = 24,47% / 3.670 pedidos / R$ 9,47M)
- [ ] **METR-02**: `src/metrics.py` responde Q3 (Categorias) ranqueando volume físico (1º Eletrônicos: 18.658, 2º Casa & Decoração: 17.899, 3º Moda: 15.680) e receita relativa em `Itens_Pedido` (1º Eletrônicos: R$ 30,80M, 2º Casa & Decoração: R$ 24,52M, 3º Beleza & Saúde: R$ 23,35M, 4º Esporte & Lazer: R$ 20,23M, 5º Moda: R$ 19,86M), explicando a posição de Moda pelo menor preço médio praticado (R$ 1.347,98)
- [ ] **METR-03**: `src/metrics.py` responde Q4 (Canais de Aquisição) calculando taxa de cancelamento por canal (`paid_search`: 30,74% = 1.219/3.965 vs. `indicação` 12,38%, `orgânico` 11,78%, `redes_sociais` 11,67%), significância estatística ($\chi^2 = 734{,}42$, $p = 7{,}22 \times 10^{-159}$) e ticket médio uniforme (~R$ 2.521–2.657; `paid_search` = R$ 2.553,51)
- [ ] **METR-04**: `src/metrics.py` responde Q5 (Evolução Mensal 2023–2024) calculando média de 551 pedidos/mês fora nov/2023, pico isolado em `2023-11` com 2.317 pedidos (4,2x a média) simétrico entre `site` (770), `app` (783) e `marketplace` (764), e `2024-11` com 585 pedidos
- [ ] **METR-05**: `src/metrics.py` responde Q7 (Fornecedores e Suporte) identificando `DeltaFornece ME` como outlier de qualidade em avaliações (nota média 2,30 vs. 3,62–3,84; 59,90% notas 1–2), demonstrando que sua taxa de tickets/100 itens (22,94) é homogênea aos pares (22,16–24,85) e que o salto de chamados em nov/2023 (375) e dez/2023 (391) ocorreu simultaneamente nos 9 fornecedores
- [ ] **METR-06**: `src/metrics.py` responde Q8 dimensionando o impacto financeiro de reestruturar `paid_search`: reduzir cancelamento de 30,74% para a média dos demais canais (~11,9%) recupera ~747 pedidos e ~R$ 1,91M em receita bruta

### Unit Testing Suite (TEST)

- [ ] **TEST-01**: `tests/test_metrics.py` valida via `pytest` todos os invariantes de integridade da base, reconciliação financeira Q6 e métricas de Ground Truth (Q1 a Q8) com 100% de aprovação

### Static Visualizations (CHRT)

- [ ] **CHRT-01**: `src/charts.py` gera gráficos estáticos PNG em alta resolução (300 DPI) em `reports/figures/` cobrindo: (1) status de pedidos e funil de conversão Q2, (2) reconciliação financeira e ticket B2B vs. B2C Q6, (3) taxa de cancelamento por canal de aquisição Q4, (4) série mensal de pedidos 2023–2024 Q5 e (5) avaliação média vs. taxa de tickets por fornecedor Q7

### Executive Notebook & Reports (EXEC)

- [ ] **EXEC-01**: Notebook executivo limpo (`notebooks/02_analise_executiva.ipynb` e `notebooks/analise_orbitshop.ipynb`) importa funções de `src/`, exibe tabelas formatadas e gráficos inline, e executa sem erros via `nbconvert --to notebook --execute --inplace`
- [ ] **EXEC-02**: Memo Executivo de 1 página gerado em `reports/memo_orbitshop.md` e `reports/memo_orbitshop.pdf` contendo no máximo 400 palavras e respondendo com precisão executiva ao comitê de Due Diligence Series C
- [ ] **EXEC-03**: `README.md` executivo documenta guia de execução em 1 comando, resumo executivo, tabela de rastreabilidade Q1–Q9 e gráficos de `reports/figures/` embutidos

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Interactive Dashboards & CI

- **DASH-01**: Dashboard interativo em Streamlit/Dash para exploração ad-hoc pelo fundo de Private Equity/VC
- **CICD-01**: Workflow GitHub Actions para execução automática de `make reproduce` a cada push

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Uso de `plotly`, `skimpy` ou `missingno` | Excluídos pelo PRD para garantir renderização nativa no GitHub e build rápido |
| Modificação do arquivo `Base_Dados_OrbitShop.xlsx` | A base bruta deve permanecer imutável para fins de auditoria |
| Remoção de `notebooks/01_eda_auditoria_exploratoria.ipynb` | Deve ser preservado como trilha histórica da investigação exploratória |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| ENV-01 | Phase 1 | Complete |
| ENV-02 | Phase 1 | Complete |
| ENV-03 | Phase 1 | Complete |
| LOAD-01 | Phase 1 | Complete |
| LOAD-02 | Phase 1 | Complete |
| AUDT-01 | Phase 1 | Pending |
| AUDT-02 | Phase 1 | Pending |
| AUDT-03 | Phase 1 | Pending |
| AUDT-04 | Phase 1 | Pending |
| METR-01 | Phase 1 | Pending |
| METR-02 | Phase 1 | Pending |
| METR-03 | Phase 1 | Pending |
| METR-04 | Phase 1 | Pending |
| METR-05 | Phase 1 | Pending |
| METR-06 | Phase 1 | Pending |
| TEST-01 | Phase 1 | Pending |
| CHRT-01 | Phase 2 | Pending |
| EXEC-01 | Phase 2 | Pending |
| EXEC-02 | Phase 2 | Pending |
| EXEC-03 | Phase 2 | Pending |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0 ✓

---
*Requirements defined: 2026-11-15*
*Last updated: 2026-11-15 after initial definition*
