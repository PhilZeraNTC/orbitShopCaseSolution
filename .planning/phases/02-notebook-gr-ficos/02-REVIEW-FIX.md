---
phase: 02-notebook-gr-ficos
fixed_at: 2026-11-15T23:23:00Z
review_path: .planning/phases/02-notebook-gr-ficos/02-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 02: Code Review Fix Report

**Fixed at:** 2026-11-15T23:23:00Z
**Source review:** .planning/phases/02-notebook-gr-ficos/02-REVIEW.md
**Iteration:** 1
**Verification location:** main checkout (`workflow.use_worktrees=false`)

**Summary:**
- Findings in scope: 3
- Fixed: 3
- Skipped: 0

## Fixed Issues

### CR-01: Prose numbers in `README.md`, `reports/memo_orbitshop.md`, and `notebooks/02_analise_executiva.ipynb` drift from code outputs and Ground Truth

**Files modified:** `README.md`, `reports/memo_orbitshop.md`, `reports/memo_orbitshop.pdf`, `notebooks/02_analise_executiva.ipynb`, `notebooks/analise_orbitshop.ipynb`
**Commit:** 05af9a2
**Applied fix:** Aligned all narrative prose figures across `README.md`, `reports/memo_orbitshop.md` (preserving `<= 400` words and re-rendering `reports/memo_orbitshop.pdf`), and the Markdown cells of `notebooks/02_analise_executiva.ipynb` (re-executed via `nbconvert` and synced to `notebooks/analise_orbitshop.ipynb`) with the deterministic Ground Truth outputs asserted in `tests/test_metrics.py`.

### WR-01: Hardcoded numeric constants in chart labels and annotations in `src/charts.py`

**Files modified:** `src/charts.py`
**Commit:** 8cc9096
**Applied fix:** Replaced hardcoded annotation literals (`788` in `plot_q2_status`, `11.94` in `plot_q4_channels`, and `2317` / `585` / `4.2` in `plot_q5_monthly`) with dynamic values computed directly from `summary` and `q4_df`.

### WR-02: `plt.close(fig)` not guarded by `try...finally` in `src/charts.py`

**Files modified:** `src/charts.py`, `reports/figures/q2_status_pedidos.png`, `reports/figures/q4_cancelamento_canais.png`, `reports/figures/q5_serie_mensal_2023_2024.png`, `reports/figures/q6_reconciliacao_b2b_b2c.png`, `reports/figures/q7_fornecedores_qualidade_tickets.png`, `reports/memo_orbitshop.pdf`
**Commit:** 2d90b8f
**Applied fix:** Wrapped figure plotting and `fig.savefig(...)` in `try: ... finally: plt.close(fig)` across `plot_q2_status`, `plot_q6_reconciliation`, `plot_q4_channels`, `plot_q5_monthly`, `plot_q7_suppliers`, and `render_memo_pdf`.

---

_Fixed: 2026-11-15T23:23:00Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_
