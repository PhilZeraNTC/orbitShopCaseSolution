---
phase: 01-core-testes
verified: 2026-11-15T20:17:50Z
status: passed
score: 9/9 must-haves verified
covered_files:
  - ".planning/phases/01-core-testes/01-01-PLAN.md"
  - ".planning/phases/01-core-testes/01-01-SUMMARY.md"
  - ".planning/phases/01-core-testes/01-02-PLAN.md"
  - ".planning/phases/01-core-testes/01-02-SUMMARY.md"
  - ".planning/phases/01-core-testes/01-03-PLAN.md"
  - ".planning/phases/01-core-testes/01-03-SUMMARY.md"
  - "Makefile"
  - "pyproject.toml"
  - "requirements.txt"
  - "src/__init__.py"
  - "src/audit.py"
  - "src/loader.py"
  - "src/metrics.py"
  - "tests/__init__.py"
  - "tests/test_metrics.py"
covered_digest: "v4:sha256:3795d281f5142166e60b0b4c1eb4b1afb46353e5e54d890e781971a4f2869825"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 1: Core & Testes Verification Report

**Phase Goal:** Construir a fundação do pacote Python (`uv`, `Makefile`, `data/`), extrair e modularizar a carga (`src/loader.py`), auditoria/reconciliação financeira (`src/audit.py`) e métricas determinísticas Q1–Q8 (`src/metrics.py`) a partir do notebook exploratório validado, comprovando 100% dos invariantes do Ground Truth com testes automatizados (`pytest`).
**Verified:** 2026-11-15T20:17:50Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | O comando `make setup` prepara o ambiente isolado via `uv` (`pyproject.toml`, `uv.lock`, `requirements.txt`) mantendo `data/Base_Dados_OrbitShop.xlsx` intacta e `notebooks/01_eda_auditoria_exploratoria.ipynb` preservado | ✓ VERIFIED | `pyproject.toml`, `uv.lock`, `requirements.txt` e `Makefile` existem; `make setup` executa `uv sync` com exit 0; SHA-256 de `data/Base_Dados_OrbitShop.xlsx` idêntico ao original |
| 2 | `src/loader.py` carrega as 6 abas tipadas sem chaves duplicadas ou órfãs (Clientes: 3.000, Produtos: 200, Pedidos: 15.000, Itens_Pedido: 36.740, Tickets_Suporte: 4.000, Avaliacoes: 8.000) | ✓ VERIFIED | `load_orbitshop_data()`, `audit_primary_keys()` e `audit_relational_integrity()` validados por `test_row_counts_and_null_invariants` e `test_relational_and_temporal_integrity` |
| 3 | `src/audit.py` reproduz exatamente a auditoria de nulos e anomalias comerciais (34.148 itens != catálogo, 2.574 abaixo do custo, 21.243 descontos sem cupom) | ✓ VERIFIED | `audit_nulls()`, `get_null_summary()` e `audit_commercial_rules()` validados por `test_row_counts_and_null_invariants` e `test_commercial_anomalies` |
| 4 | `src/audit.py` executa a reconciliação financeira Q6 (`Pedidos.valor_total` R$ 38.418.252,65 vs `Itens_Pedido` R$ 165.878.066,67; 0 de 14.921 conciliam; ticket B2B = 6,15x B2C após imputação dos 79 nulos) | ✓ VERIFIED | `reconcile_orders_vs_items()` e `audit_q6_by_segment()` validados por `test_q6_financial_reconciliation` |
| 5 | `src/metrics.py` calcula de forma determinística o paradoxo Camila vs. Rogério (16,91% global; 16,78% em 2023; 17,08% em 2024) e a distribuição de status Q2 (entregue 9.959, cancelado 2.537, em_transito 1.371 sendo 788 de 2023, devolvido 1.133; não convertidos = 24,47% / R$ 9,47M) | ✓ VERIFIED | `metrics_camila_vs_rogerio()` e `metrics_q2_status()` validados por `test_paradox_and_q2_status` |
| 6 | `src/metrics.py` calcula o ranking de categorias Q3 por volume físico (Eletrônicos 18.658, Casa & Decoração 17.899, Moda 15.680) vs. receita relativa e preço médio de Moda (R$ 1.347,98) | ✓ VERIFIED | `metrics_q3_categories()` validado por `test_q3_categories` |
| 7 | `src/metrics.py` calcula o cancelamento por canal de aquisição Q4 (`paid_search` = 30,74%, qui-quadrado = 734,42, ticket médio R$ 2.553,51) e a série mensal Q5 (média 551 pedidos/mês fora nov/2023; pico 2.317 em 2023-11; 585 em 2024-11) | ✓ VERIFIED | `metrics_q4_channels()` e `metrics_q5_monthly()` validados por `test_q4_acquisition_channels` e `test_q5_monthly_evolution` |
| 8 | `src/metrics.py` calcula as métricas de fornecedores Q7 (`DeltaFornece ME` nota 2,30, 59,90% notas 1-2, 22,94 tickets/100 itens; salto de 375 e 391 chamados em nov-dez/2023) e o dimensionamento Q8 (~747 pedidos e ~R$ 1,91M recuperáveis) | ✓ VERIFIED | `metrics_q7_suppliers()` e `metrics_q8_recommendation()` validados por `test_q7_suppliers_and_support` e `test_q8_recommendation_sizing` |
| 9 | O comando `make test` executa `pytest` em `tests/test_metrics.py` e aprova 100% dos 11 testes de invariantes numéricos e regras de negócio em menos de 30s | ✓ VERIFIED | `make test` executou `uv run pytest -v` com `11 passed in 5.90s`; `uv run ruff check src tests` retornou `All checks passed!` |

**Score:** 9/9 truths verified (0 present, behavior-unverified)

## Artifact & Key-Link Verification

- **Artifacts (`verify.artifacts`):** 7/7 passed (`pyproject.toml`, `requirements.txt`, `Makefile`, `src/loader.py`, `src/audit.py`, `src/metrics.py`, `tests/test_metrics.py`)
- **Key Links (`verify.key-links`):** 7/7 verified

## Requirements Coverage (Phase 1)

| Requirement | Status | Evidence |
|-------------|--------|----------|
| `ENV-01` | ✓ SATISFIED | `pyproject.toml`, `uv.lock`, `requirements.txt` |
| `ENV-02` | ✓ SATISFIED | `Makefile` (`setup`, `test`, `reproduce`, `all`) |
| `ENV-03` | ✓ SATISFIED | `data/Base_Dados_OrbitShop.xlsx` & `notebooks/01_eda_auditoria_exploratoria.ipynb` (`test_raw_data_file_integrity`) |
| `LOAD-01` | ✓ SATISFIED | `src/loader.py#load_orbitshop_data` (`test_row_counts_and_null_invariants`) |
| `LOAD-02` | ✓ SATISFIED | `src/loader.py#audit_relational_integrity` (`test_relational_and_temporal_integrity`) |
| `AUDT-01` | ✓ SATISFIED | `src/audit.py#get_null_summary` (`test_row_counts_and_null_invariants`) |
| `AUDT-02` | ✓ SATISFIED | `src/audit.py#audit_commercial_rules` (`test_commercial_anomalies`) |
| `AUDT-03` | ✓ SATISFIED | `src/audit.py#reconcile_orders_vs_items` (`test_q6_financial_reconciliation`) |
| `AUDT-04` | ✓ SATISFIED | `src/audit.py#audit_q6_by_segment` (`test_q6_financial_reconciliation`) |
| `METR-01` | ✓ SATISFIED | `src/metrics.py#metrics_camila_vs_rogerio`, `metrics_q2_status` (`test_paradox_and_q2_status`) |
| `METR-02` | ✓ SATISFIED | `src/metrics.py#metrics_q3_categories` (`test_q3_categories`) |
| `METR-03` | ✓ SATISFIED | `src/metrics.py#metrics_q4_channels` (`test_q4_acquisition_channels`) |
| `METR-04` | ✓ SATISFIED | `src/metrics.py#metrics_q5_monthly` (`test_q5_monthly_evolution`) |
| `METR-05` | ✓ SATISFIED | `src/metrics.py#metrics_q7_suppliers` (`test_q7_suppliers_and_support`) |
| `METR-06` | ✓ SATISFIED | `src/metrics.py#metrics_q8_recommendation` (`test_q8_recommendation_sizing`) |
| `TEST-01` | ✓ SATISFIED | `tests/test_metrics.py` (`11 passed in 5.90s`) |

## Anti-Patterns & Prohibitions Check

- **Debt markers (`TBD`, `FIXME`, `XXX`, `TODO`, `HACK`):** 0 encontrados em `src/` e `tests/`.
- **Prohibitions:**
  - Sem `plotly`, `skimpy` ou `missingno` em `pyproject.toml`, `requirements.txt` ou `src/` (`VERIFIED`).
  - `data/Base_Dados_OrbitShop.xlsx` e `notebooks/01_eda_auditoria_exploratoria.ipynb` intactos (`VERIFIED`).
  - `Pedidos.valor_total` utilizado como fonte oficial de receita/ticket para Q2, Q4 e Q8 (`VERIFIED`).
  - Sem mocks de dados em `tests/test_metrics.py` (`VERIFIED`).

