# Walking Skeleton: Phase 2 — Notebook & Gráficos

## Phase Goal (User Story)
**As a** Due Diligence Partner and Series C Investment Committee member, **I want to** inspect high-resolution 300 DPI static charts (`reports/figures/`), a clean executed executive Jupyter Notebook (`notebooks/02_analise_executiva.ipynb` / `notebooks/analise_orbitshop.ipynb`), a 1-page Executive Memo (`reports/memo_orbitshop.md` and `.pdf` <= 400 words), and an executive `README.md`, **so that** the entire OrbitShop Q1–Q9 analysis can be reviewed and reproduced in a single command (`make all`).

## Tracer Slices (First Task of Each Plan)
1. **Plan 02-01 Task 1 (`type="tracer"`)**: End-to-end static visualization generator `src/charts.py` consuming `src/loader.py`, `src/audit.py`, and `src/metrics.py` to produce all 5 high-resolution 300 DPI PNG figures in `reports/figures/`.
2. **Plan 02-02 Task 1 (`type="tracer"`)**: End-to-end 1-page Executive Memo in `reports/memo_orbitshop.md` (`<= 400` words) and deterministic PDF export to `reports/memo_orbitshop.pdf`.
