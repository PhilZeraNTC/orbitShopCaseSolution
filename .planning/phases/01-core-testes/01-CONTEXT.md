# Phase 1: Core & Testes - Context

**Gathered:** 2026-11-15
**Status:** Ready for planning
**Source:** PRD Express Path (`PRD.md` + `notebooks/01_eda_auditoria_exploratoria.ipynb`)

<domain>
## Phase Boundary

Construir a fundação do pacote Python (`uv`, `pyproject.toml`, `uv.lock`, `requirements.txt`, `Makefile`, `data/Base_Dados_OrbitShop.xlsx`), extrair e modularizar as funções de carga (`src/loader.py`), auditoria/reconciliação financeira (`src/audit.py`) e métricas determinísticas Q1–Q8 (`src/metrics.py`) a partir de `notebooks/01_eda_auditoria_exploratoria.ipynb`, e validar 100% dos invariantes numéricos do Ground Truth com testes automatizados (`tests/test_metrics.py` via `pytest`).

</domain>

<decisions>
## Implementation Decisions

### Environment & Automation
- **D-01:** Gerenciar dependências com `uv` (`pyproject.toml` + `uv.lock`) e manter `requirements.txt` espelhado com as dependências enxutas (`pandas`, `openpyxl`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `jupyter`, `nbconvert`, `pytest`, `ruff`), sem usar `plotly`, `skimpy` ou `missingno`.
- **D-02:** Disponibilizar a base bruta intacta em `data/Base_Dados_OrbitShop.xlsx` (preservando o arquivo original sem mutação) e preservar `notebooks/01_eda_auditoria_exploratoria.ipynb` intacto como histórico de auditoria.
- **D-03:** Implementar `Makefile` com alvos `setup`, `test`, `reproduce` e `all`.

### Data Loader & Relational Integrity (`src/loader.py`)
- **D-04:** Carregar e tipar as 6 abas transacionais de `data/Base_Dados_OrbitShop.xlsx` (`Clientes`: 3.000 linhas, `Produtos`: 200 linhas, `Pedidos`: 15.000 linhas, `Itens_Pedido`: 36.740 linhas, `Tickets_Suporte`: 4.000 linhas, `Avaliacoes`: 8.000 linhas), convertendo colunas de data (`data_cadastro`, `data_pedido`, `data_abertura`, `data_resolucao`, `data_avaliacao`) com `pd.to_datetime` e validando 0 chaves primárias duplicadas e 0 chaves estrangeiras órfãs.

### Audit & Financial Reconciliation (`src/audit.py`)
- **D-05:** Auditar nulos (`Pedidos.valor_total`: 79 nulos = 0,53%; `Itens_Pedido.desconto_aplicado`: 301 nulos = 0,82%; `Tickets_Suporte.data_resolucao`: 1.653 nulos = 41,33%; `Avaliacoes.comentario`: 1.679 nulos = 20,99%) e anomalias comerciais (`preco_praticado` != `preco_unitario` em 34.148 itens; 2.574 itens vendidos abaixo do custo; 21.243 descontos aplicados sem cupom).
- **D-06:** Implementar a reconciliação financeira Q6 comprovando que 0 de 14.921 pedidos válidos conciliam (±R$ 0,05) entre `Pedidos.valor_total` (soma R$ 38.418.252,65) e a soma líquida de `Itens_Pedido` (R$ 165.878.066,67; diferença -R$ 127.459.814,02), imputar os 79 nulos de `Pedidos.valor_total` pela mediana do segmento (`B2B` = R$ 7.803,97 para 13 nulos; `B2C` = R$ 1.255,37 para 66 nulos) e demonstrar ticket médio B2B = 6,15x B2C (R$ 7.778,34 vs. R$ 1.264,72).

### Deterministic Business Metrics (`src/metrics.py`) & Pytest (`tests/test_metrics.py`)
- **D-07:** Implementar funções puras e determinísticas em `src/metrics.py` para o paradoxo Camila vs. Rogério e questões Q2, Q3, Q4, Q5, Q7 e Q8, validadas integralmente por `tests/test_metrics.py` via `pytest`.

### the agent's Discretion
- Assinaturas exatas de funções auxiliares internas e tipos de retorno (DataFrames/dicts/dataclasses) em `src/loader.py`, `src/audit.py` e `src/metrics.py`, desde que sejam determinísticos, bem tipados e facilmente consumíveis tanto por `tests/test_metrics.py` quanto pelo notebook executivo da Fase 2.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Especificação e Regras de Negócio
- `PRD.md` — Especificação completa da arquitetura, stack obrigatória, estrutura de diretórios e invariantes numéricos de Ground Truth (Q1 a Q9)
- `notebooks/01_eda_auditoria_exploratoria.ipynb` — Implementação exploratória de referência validada pelo autor com todas as agregações e fórmulas exatas

### Planejamento do Projeto
- `.planning/PROJECT.md` — Contexto geral, decisões e restrições do projeto
- `.planning/REQUIREMENTS.md` — Requisitos `ENV-01..03`, `LOAD-01..02`, `AUDT-01..04`, `METR-01..06` e `TEST-01`
- `.planning/ROADMAP.md` — Critérios de sucesso e estrutura dos 3 planos da Fase 1

</canonical_refs>

<specifics>
## Specific Ideas

- Manter compatibilidade do caminho da base de dados (`data/Base_Dados_OrbitShop.xlsx` como caminho canônico do PRD, copiando `Base_Dados_OrbitShop.xlsx` para `data/Base_Dados_OrbitShop.xlsx` sem remover a cópia da raiz para não quebrar referências legadas).
- Nas métricas de `src/metrics.py`, retornar tanto tabelas prontas para exibição (DataFrames) quanto dicionários/valores escalares das métricas-chave para asserção direta em `tests/test_metrics.py`.

</specifics>

<deferred>
## Deferred Ideas

- Geração dos gráficos estáticos em 300 DPI (`src/charts.py` -> `reports/figures/`) — Fase 2
- Construção e execução do notebook executivo (`notebooks/02_analise_executiva.ipynb` / `notebooks/analise_orbitshop.ipynb`) — Fase 2
- Redação do Memo Executivo (`reports/memo_orbitshop.md` e `.pdf`) e `README.md` final — Fase 2

</deferred>

---

*Phase: 01-core-testes*
*Context gathered: 2026-11-15 via PRD Express Path*
