---
phase: 01-core-testes
fixed_at: 2026-11-15T23:06:00Z
review_path: .planning/phases/01-core-testes/01-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 01: Code Review Fix Report

**Fixed at:** 2026-11-15T23:06:00Z
**Source review:** .planning/phases/01-core-testes/01-REVIEW.md
**Iteration:** 1
**Verification location:** main checkout (`workflow.use_worktrees=false`)

**Summary:**
- Findings in scope: 4
- Fixed: 4
- Skipped: 0

## Fixed Issues

### WR-01: Unfilled left-join NaNs in `reconcile_orders_vs_items` when an order has zero items

**Files modified:** `src/audit.py`
**Commit:** 669b133
**Applied fix:** Filled `NaN` values after left-merging `agg_itens` onto `pedidos` (`qtd_itens` and `unidades` defaulted to `0`, monetary totals to `0.0`, and `tem_desc_nulo` to `False`) before computing `diff_liquida` and `diff_bruta`.

### WR-02: Unfilled `NaN` in `receita_nao_cancelada` merge in `metrics_q3_categories`

**Files modified:** `src/metrics.py`
**Commit:** 2564624
**Applied fix:** Added `q3_df["receita_nao_cancelada"] = q3_df["receita_nao_cancelada"].fillna(0.0)` immediately after left-merging `receita_nao_cancelada`.

### WR-03: Unfilled `NaN` in supplier ticket/review left-merges in `metrics_q7_suppliers`

**Files modified:** `src/metrics.py`
**Commit:** e1b88fe
**Applied fix:** Filled `NaN` with `0` (and cast to `int`) on `qtd_avaliacoes`, `tickets_associados`, and `tickets_defeito_troca` after merging `aval_forn` and `tkt_forn_agg` onto `vendas_forn`.

### WR-04: `Makefile` target `reproduce` runs `test` before regenerating figures and notebook outputs

**Files modified:** `Makefile`
**Commit:** a4a75c5
**Applied fix:** Updated `reproduce` in `Makefile` to run `src.charts` and `nbconvert --execute` first and then invoke `$(MAKE) test` so regenerated artifacts are always verified after creation.

---

_Fixed: 2026-11-15T23:06:00Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_
