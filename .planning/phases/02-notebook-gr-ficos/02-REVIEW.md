---
phase: 02-notebook-gr-ficos
reviewed: 2026-11-15T23:11:00Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - README.md
  - notebooks/02_analise_executiva.ipynb
  - notebooks/analise_orbitshop.ipynb
  - reports/memo_orbitshop.md
  - src/charts.py
  - tests/test_metrics.py
findings:
  critical: 1
  warning: 2
  info: 1
  total: 4
  necessity: 1
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-11-15T23:11:00Z
**Depth:** standard
**Files Reviewed:** 6
**Status:** issues_found

## Narrative Findings (AI reviewer)

## Summary

Reviewed the 6 source, notebook, documentation, and test files modified in Phase 02 (`02-notebook-gr-ficos`) at `standard` depth (excluding binary PNG/PDF outputs). Found 1 critical issue (`CR-01`) where prose numbers in `README.md`, `reports/memo_orbitshop.md`, and Markdown cells of `notebooks/02_analise_executiva.ipynb` drifted from the Ground Truth outputs produced by the code cells and asserted in `tests/test_metrics.py`. Also found 2 warnings (`WR-01`, `WR-02`) in `src/charts.py` regarding hardcoded annotation constants and unguarded `plt.close(fig)` calls, plus 1 informational necessity finding (`IN-01`).

## Critical Issues

### CR-01: Prose numbers in `README.md`, `reports/memo_orbitshop.md`, and `notebooks/02_analise_executiva.ipynb` drift from code outputs and Ground Truth

**File:** `README.md:55-76`
**Issue:** Several narrative prose numbers in `README.md`, `reports/memo_orbitshop.md`, and the Markdown cells of `notebooks/02_analise_executiva.ipynb` (`notebooks/analise_orbitshop.ipynb`) do not match the deterministic values computed by `src/` and verified by `tests/test_metrics.py`:
- Null counts in prose state `Itens_Pedido.desconto_aplicado (1.839 = 5,01%)`, `Tickets_Suporte.data_resolucao (418 = 10,45%)`, and `Avaliacoes.comentario (1.825 = 22,81%)`, whereas the dataset and code outputs have `301 (0,82%)`, `1.653 (41,33%)`, and `1.679 (20,99%)`, and `Pedidos.valor_total` nulls split into `13 B2B` and `66 B2C` (not `14/65` or `16/63`).
- Single-item orders in prose state `4.790` instead of `4.408`.
- Cancelled orders in prose state `2.536` (`3.669` non-converted = `24,46%`) instead of `2.537` (`3.670` non-converted = `24,47%`, official non-converted revenue `R$ 9.467.259,31`).
**Fix:**
Update `README.md`, `reports/memo_orbitshop.md` (preserving `<= 400` words and re-rendering `reports/memo_orbitshop.pdf`), and the Markdown cells in `notebooks/02_analise_executiva.ipynb` (re-executing and syncing to `notebooks/analise_orbitshop.ipynb`) so 100% of prose numbers match the Ground Truth invariants in `tests/test_metrics.py`.

## Warnings

### WR-01: Hardcoded numeric constants in chart labels and annotations in `src/charts.py`

**File:** `src/charts.py:72-402`
**Issue:** `plot_q2_status` hardcodes `788` in `"Em Trânsito\n(788 de 2023)"` (line 72), `plot_q4_channels` hardcodes `11.94` in `ax1.axhline(11.94, ...)` (line 273), and `plot_q5_monthly` hardcodes `2317` and `585` in annotations and percentage division (lines 371–402) instead of reading those values dynamically from `summary` and `q4_df`.
**Fix:**
```python
    # In plot_q2_status:
    "em_transito": f"Em Trânsito\n({summary['em_transito_2023']} de 2023)",
    # In plot_q4_channels:
    other_df = q4_df[q4_df["canal_aquisicao"] != "paid_search"]
    bench_pct = float(other_df["cancelados"].sum() / other_df["pedidos"].sum() * 100.0)
    ax1.axhline(bench_pct, ...)
    # In plot_q5_monthly:
    ped_nov23 = int(summary["pedidos_nov_2023"])
    ped_nov24 = int(summary["pedidos_nov_2024"])
```

### WR-02: `plt.close(fig)` not guarded by `try...finally` in `src/charts.py`

**File:** `src/charts.py:84-141`
**Issue:** Each `plot_*` function and `render_memo_pdf` creates a `matplotlib` figure and calls `plt.close(fig)` only after plotting and `fig.savefig(...)`. If an exception is raised before `plt.close(fig)`, the figure remains open in `matplotlib`'s global state.
**Fix:**
Wrap the plotting and `fig.savefig(out_path, ...)` blocks in `try: ... finally: plt.close(fig)` across `plot_q2_status`, `plot_q6_reconciliation`, `plot_q4_channels`, `plot_q5_monthly`, `plot_q7_suppliers`, and `render_memo_pdf`.

## Info

### IN-01: Already-defended-elsewhere — redundant `enrich_items` and `reconcile_orders_vs_items` calls in `generate_all_charts`

**File:** `src/charts.py:596-598`
**Category:** necessity
**Issue:** `generate_all_charts` calls `enrich_items` and `reconcile_orders_vs_items` and then calls `build_orders_analytical_df(data)`, which internally calls `enrich_items` and `reconcile_orders_vs_items` a second time on the same data.
**Fix:** Reuse `df_pedidos` (which already contains all columns of `rec` plus segment/date enrichments) for `plot_q6_reconciliation`.

---

_Reviewed: 2026-11-15T23:11:00Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
