---
phase: 01
review: 01-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "Unfilled left-join NaNs in `reconcile_orders_vs_items` when an order has zero items"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "Unfilled `NaN` in `receita_nao_cancelada` merge in `metrics_q3_categories`"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "Unfilled `NaN` in supplier ticket/review left-merges in `metrics_q7_suppliers`"
  - id: WR-04
    severity: warning
    disposition: fixed
    title: "`Makefile` target `reproduce` runs `test` before regenerating figures and notebook outputs"
  - id: IN-01
    severity: info
    disposition: open
    title: "Generality without instantiation — unused `ratio_preco` column in `enrich_items`"
  - id: IN-02
    severity: info
    disposition: open
    title: "Phantom requirement — unused `clientes` parameter in `reconcile_orders_vs_items`"
open: 2
total: 6
recorded: 2026-11-15T23:06:35.277Z
---

# Phase 01: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 01-REVIEW-FIX.md |
| WR-02 | warning | fixed | 01-REVIEW-FIX.md |
| WR-03 | warning | fixed | 01-REVIEW-FIX.md |
| WR-04 | warning | fixed | 01-REVIEW-FIX.md |
| IN-01 | info | open | - |
| IN-02 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
