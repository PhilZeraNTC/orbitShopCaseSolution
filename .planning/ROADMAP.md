# Roadmap: OrbitShop Due Diligence Series C

## Overview

Este roadmap estrutura a construção do repositório auditável de Due Diligence Series C da OrbitShop em duas fases enxutas e determinísticas: a **Fase 1 (Core & Testes)** estabelece o ambiente reprodutível (`uv` + `Makefile`), modulariza a carga, auditoria e métricas de negócio (Q1–Q8) a partir da investigação exploratória validada (`notebooks/01_eda_auditoria_exploratoria.ipynb`) e trava 100% dos invariantes numéricos com testes automatizados (`pytest`); a **Fase 2 (Notebook & Gráficos)** produz os gráficos estáticos em 300 DPI (`reports/figures/`), o Jupyter Notebook executivo executado (`notebooks/02_analise_executiva.ipynb` / `notebooks/analise_orbitshop.ipynb`), o Memo Executivo de 1 página (`reports/memo_orbitshop.md` e `.pdf`, máx. 400 palavras) e o `README.md` executivo final.

## Phases

**Phase Numbering:**
- Integer phases (1, 2): Planned milestone work
- Decimal phases (1.1, 1.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Core & Testes** - Fundação do ambiente (`uv`/`Makefile`), módulos `src/loader.py`, `src/audit.py`, `src/metrics.py` e suíte `pytest` validando o Ground Truth (Q1–Q8) (completed 2026-11-15)
- [x] **Phase 2: Notebook & Gráficos** - Gráficos estáticos 300 DPI (`src/charts.py`), notebook executivo executado, Memo Executivo de 1 página (MD/PDF <= 400 palavras) e `README.md` (completed 2026-11-15)

## Phase Details

### Phase 1: Core & Testes
**Goal**: Construir a fundação do pacote Python (`uv`, `Makefile`, `data/`), extrair e modularizar a carga (`src/loader.py`), auditoria/reconciliação financeira (`src/audit.py`) e métricas determinísticas Q1–Q8 (`src/metrics.py`) a partir do notebook exploratório validado, comprovando 100% dos invariantes do Ground Truth com testes automatizados (`pytest`).
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: ENV-01, ENV-02, ENV-03, LOAD-01, LOAD-02, AUDT-01, AUDT-02, AUDT-03, AUDT-04, METR-01, METR-02, METR-03, METR-04, METR-05, METR-06, TEST-01
**Success Criteria** (what must be TRUE):
  1. O comando `make setup` prepara o ambiente isolado via `uv` (`pyproject.toml`, `uv.lock`, `requirements.txt`) mantendo `data/Base_Dados_OrbitShop.xlsx` intacta e `notebooks/01_eda_auditoria_exploratoria.ipynb` preservado.
  2. `src/loader.py` e `src/audit.py` carregam as 6 abas tipadas sem chaves duplicadas ou órfãs e reproduzem exatamente a auditoria de nulos, anomalias comerciais (21.243 descontos sem cupom, 2.574 itens abaixo do custo) e reconciliação financeira Q6 (`Pedidos.valor_total` R$ 38.418.252,65 vs `Itens_Pedido` R$ 165.878.066,67; ticket B2B = 6,15x B2C após imputação dos 79 nulos).
  3. `src/metrics.py` retorna de forma pura e determinística todos os indicadores validados para o paradoxo Camila vs. Rogério e para as questões Q2, Q3, Q4, Q5, Q7 e Q8.
  4. O comando `make test` executa `pytest` em `tests/test_metrics.py` e aprova 100% dos testes de invariantes numéricos e regras de negócio do Ground Truth.
**Plans**: 3/3 plans complete

Plans:
**Wave 1**
- [x] 01-01-PLAN.md — Setup do ambiente (`pyproject.toml`, `uv.lock`, `requirements.txt`, `Makefile`, `data/Base_Dados_OrbitShop.xlsx`) e módulo `src/loader.py`

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 01-02-PLAN.md — Implementação de `src/audit.py` (nulos, anomalias comerciais e reconciliação Q6) e `src/metrics.py` (paradoxo C-level e Q2–Q8)

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 01-03-PLAN.md — Suíte de testes unitários `tests/test_metrics.py` (`pytest`) validando todos os invariantes do PRD e verificação via `make test`

### Phase 2: Notebook & Gráficos
**Goal**: Gerar as visualizações estáticas em alta resolução (`src/charts.py` -> `reports/figures/` em 300 DPI), o Jupyter Notebook executivo limpo e executado (`notebooks/02_analise_executiva.ipynb` e `notebooks/analise_orbitshop.ipynb`), o Memo Executivo de 1 página (`reports/memo_orbitshop.md` e `reports/memo_orbitshop.pdf`, máx. 400 palavras) e o `README.md` executivo final validado via `make reproduce` e `make all`.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: CHRT-01, EXEC-01, EXEC-02, EXEC-03
**Success Criteria** (what must be TRUE):
  1. `src/charts.py` gera todos os gráficos estáticos PNG em 300 DPI em `reports/figures/` (status de pedidos Q2, reconciliação B2B/B2C Q6, cancelamento por canal Q4, série mensal 2023–2024 Q5 e qualidade/tickets por fornecedor Q7).
  2. O comando `make reproduce` executa os testes e roda o notebook executivo (`notebooks/02_analise_executiva.ipynb` e `notebooks/analise_orbitshop.ipynb`) via `nbconvert --to notebook --execute --inplace` sem erros, salvando tabelas formatadas e gráficos inline.
  3. O Memo Executivo de 1 página existe em `reports/memo_orbitshop.md` e `reports/memo_orbitshop.pdf` respeitando o limite estrito de no máximo 400 palavras.
  4. `README.md` apresenta guia de execução em 1 comando, resumo executivo, tabela de rastreabilidade Q1–Q9 e gráficos embutidos, com `make all` concluindo ponta a ponta com sucesso.
**Plans**: 2/2 plans complete

Plans:
**Wave 1**
- [x] 02-01-PLAN.md — Módulo `src/charts.py` (PNGs 300 DPI em `reports/figures/`) e construção/execução do notebook executivo (`notebooks/02_analise_executiva.ipynb` e `notebooks/analise_orbitshop.ipynb`)

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 02-02-PLAN.md — Redação e exportação do Memo Executivo de 1 página (`reports/memo_orbitshop.md` e `.pdf` <= 400 palavras), `README.md` executivo e validação `make all`

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core & Testes | 3/3 | Complete    | 2026-11-15 |
| 2. Notebook & Gráficos | 2/2 | Complete    | 2026-11-15 |
