# Phase 2: Notebook & Gráficos - Context

**Gathered:** 2026-11-15
**Status:** Ready for planning
**Source:** PRD Express Path (`PRD.md` + `notebooks/01_eda_auditoria_exploratoria.ipynb` + Phase 1 `src/`)

<domain>
## Phase Boundary

Gerar as visualizações estáticas em alta resolução (`src/charts.py` -> `reports/figures/` em 300 DPI), construir e executar o Jupyter Notebook executivo limpo (`notebooks/02_analise_executiva.ipynb` e `notebooks/analise_orbitshop.ipynb`) importando `src/`, redigir e exportar o Memo Executivo de 1 página (`reports/memo_orbitshop.md` e `reports/memo_orbitshop.pdf`, máx. 400 palavras) e o `README.md` executivo final, validando a reprodutibilidade ponta a ponta via `make reproduce` e `make all`.

</domain>

<decisions>
## Implementation Decisions

### Static High-Resolution Visualizations (`src/charts.py`)
- **D-01:** Implementar `src/charts.py` usando exclusivamente `matplotlib` e `seaborn` (backend não-interativo `Agg`, sem `plotly`, `skimpy` ou `missingno`) para gerar e salvar em `reports/figures/` (300 DPI, `bbox_inches="tight"`) os 5 gráficos executivos:
  1. `reports/figures/q2_status_pedidos.png` — Distribuição de status de pedidos (Q2: entregue 66,39%, cancelado 16,91%, em_transito 9,14% com destaque aos 788 de 2023, devolvido 7,55%) e funil de não-conversão (24,47% / R$ 9,47M).
  2. `reports/figures/q6_reconciliacao_b2b_b2c.png` — Reconciliação financeira Q6: ticket médio `Pedidos.valor_total` (B2B R$ 7.778,34 = 6,15x B2C R$ 1.264,72) vs. soma líquida distorcida de `Itens_Pedido` (~R$ 11.000 em ambos os segmentos).
  3. `reports/figures/q4_cancelamento_canais.png` — Taxa de cancelamento e ticket médio por canal de aquisição (Q4: `paid_search` 30,74% vs. ~11,7%–12,4% nos demais canais; $\chi^2 = 734,42$).
  4. `reports/figures/q5_serie_mensal_2023_2024.png` — Evolução mensal de pedidos e taxa de cancelamento 2023–2024 (Q5: média de 551 pedidos/mês fora nov/2023; pico isolado de 2.317 pedidos em `2023-11` = 4,2x a média, simétrico entre `site` 770, `app` 783 e `marketplace` 764; `2024-11` com 585 pedidos).
  5. `reports/figures/q7_fornecedores_qualidade_tickets.png` — Qualidade de avaliações vs. taxa de tickets/100 itens por fornecedor e evolução mensal de chamados (Q7: `DeltaFornece ME` nota 2,30 e 59,90% notas 1–2 vs. 3,62–3,84 dos pares, porém taxa de tickets homogênea em 22,94/100 itens; salto sistêmico em nov/2023 = 375 e dez/2023 = 391).
- **D-02:** Expor `generate_all_charts()` e ponto de entrada `python -m src.charts` retornando o dicionário de caminhos dos 5 arquivos PNG gerados.

### Executive Jupyter Notebook (`notebooks/02_analise_executiva.ipynb` & `notebooks/analise_orbitshop.ipynb`)
- **D-03:** Construir o notebook narrativo limpo em `notebooks/02_analise_executiva.ipynb` importando `src.loader`, `src.audit`, `src.metrics` e `src.charts`, estruturado para responder com clareza executiva ao paradoxo Camila vs. Rogério e às questões Q1 a Q9, exibindo tabelas formatadas e gráficos inline.
- **D-04:** Executar o notebook inplace via `uv run jupyter nbconvert --to notebook --execute --inplace notebooks/02_analise_executiva.ipynb` e sincronizar uma cópia idêntica já executada em `notebooks/analise_orbitshop.ipynb` (garantindo compatibilidade com ambas as nomenclaturas citadas nas seções 1 e 2 do `PRD.md`), mantendo `notebooks/01_eda_auditoria_exploratoria.ipynb` intacto.

### 1-Page Executive Memo (`reports/memo_orbitshop.md` & `reports/memo_orbitshop.pdf`)
- **D-05:** Redigir `reports/memo_orbitshop.md` com **no máximo 400 palavras** (verificado programaticamente via `wc -w <= 400`), sintetizando para o Comitê de Investimento Series C: (1) Diagnóstico de Integridade & Fonte da Verdade Financeira (Q1/Q6), (2) Resolução do Paradoxo Growth vs. CFO e Gargalos Operacionais (Q2/Q3/Q4/Q5/Q7), e (3) Recomendação Prioritária Única (Q8: reestruturar `paid_search` recuperando ~747 pedidos e ~R$ 1,91M em receita bruta) e próximos passos de governança de dados (Q9).
- **D-06:** Gerar `reports/memo_orbitshop.pdf` (1 página A4) de forma determinística a partir do conteúdo de `reports/memo_orbitshop.md` e atualizar o `Makefile` para garantir que `make reproduce` e `make all` regenerem gráficos, notebook executado e PDF sem erros.

### Executive `README.md`
- **D-07:** Escrever o `README.md` executivo na raiz do projeto contendo: visão geral do case de Due Diligence Series C (OrbitShop | Peers Consulting & Technology), instruções de reprodução em 1 comando (`make all` / `make reproduce` / `make test`), síntese executiva dos achados, tabela de rastreabilidade completa Q1–Q9 (questão, descoberta, evidência numérica e artefato/função correspondente) e incorporação direta dos 5 gráficos de `reports/figures/*.png`.

### the agent's Discretion
- Paleta de cores corporativa (azul-marinho/cinza para séries base, vermelho/coral para anomalias e destaques como `paid_search`, `2023-11` e `DeltaFornece ME`) e layout tipográfico do PDF de 1 página.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Especificação e Entregáveis da Fase 1
- `PRD.md` — Especificação completa de arquitetura, entregáveis e invariantes numéricos (Seções 1, 2 e 3)
- `src/loader.py`, `src/audit.py`, `src/metrics.py` — Módulos analíticos implementados e validados na Fase 1
- `tests/test_metrics.py` — Suíte de testes unitários validando todos os números-chave
- `Makefile` — Automação existente (`setup`, `test`, `reproduce`, `all`)

### Planejamento do Projeto
- `.planning/PROJECT.md` — Contexto geral e restrições
- `.planning/REQUIREMENTS.md` — Requisitos `CHRT-01`, `EXEC-01`, `EXEC-02` e `EXEC-03`
- `.planning/ROADMAP.md` — Critérios de sucesso e estrutura dos 2 planos da Fase 2 (`02-01` e `02-02`)

</canonical_refs>

<specifics>
## Specific Ideas

- Usar `matplotlib.use("Agg")` no topo de `src/charts.py` para execução headless determinística tanto em CLI (`python -m src.charts`) quanto via `nbconvert`.
- Incluir verificação automatizada de contagem de palavras (`<= 400` palavras) para `reports/memo_orbitshop.md` e verificação de cabeçalho `%PDF` e tamanho não-vazio para `reports/memo_orbitshop.pdf`.

</specifics>

<deferred>
## Deferred Ideas

- Nenhuma — a Fase 2 conclui 100% do escopo v1 do projeto.

</deferred>

---

*Phase: 02-notebook-gr-ficos*
*Context gathered: 2026-11-15 via PRD Express Path*
