# Walking Skeleton — OrbitShop Due Diligence Series C

**Phase:** 1
**Generated:** 2026-11-15

## Capability Proven End-to-End

> Um analista de Due Diligence consegue provisionar o ambiente isolado via `make setup` (`uv`), carregar de forma tipada as 6 abas de `data/Base_Dados_OrbitShop.xlsx` via `src/loader.py`, auditar e reconciliar a receita de `Pedidos` vs. `Itens_Pedido` via `src/audit.py`, calcular todas as métricas Q1–Q8 via `src/metrics.py` e validar 100% dos invariantes numéricos com `make test` (`pytest`).

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Gerenciador de pacotes e ambiente | `uv` (`pyproject.toml` + `uv.lock`) + `requirements.txt` espelhado | Reprodutibilidade determinística com lockfile e compatibilidade universal com `pip` (D-01) |
| Camada de dados (`src/loader.py`) | `pandas` + `openpyxl` lendo `data/Base_Dados_OrbitShop.xlsx` (somente leitura) | Preserva a base original intacta e garante tipagem explícita de datas e chaves (D-02, D-04) |
| Camada de auditoria e reconciliação (`src/audit.py`) | Funções puras para auditoria de nulos, regras comerciais e reconciliação Q6 com imputação por mediana do segmento (`B2B`/`B2C`) | Isola a regra crítica de fonte oficial da verdade financeira (`Pedidos.valor_total`) do cálculo das métricas analíticas (D-05, D-06) |
| Camada de métricas (`src/metrics.py`) | Funções puras e determinísticas usando `pandas`, `numpy` e `scipy.stats` | Garante paridade numérica 100% com `notebooks/01_eda_auditoria_exploratoria.ipynb` e testabilidade direta via `pytest` (D-07) |
| Orquestração local (`Makefile`) | Alvos `setup`, `test`, `reproduce`, `all` | Permite execução auditável em 1 comando conforme exigido pelo PRD (D-03) |

## Stack Touched in Phase 1

- [x] Project scaffold (`pyproject.toml`, `uv.lock`, `requirements.txt`, `Makefile`, `src/__init__.py`, `tests/__init__.py`)
- [x] Data ingestion & integrity validation (`src/loader.py` lendo `data/Base_Dados_OrbitShop.xlsx`)
- [x] Financial reconciliation & commercial rules audit (`src/audit.py`)
- [x] Analytical metrics engine Q1–Q8 (`src/metrics.py`)
- [x] Automated invariant test suite (`tests/test_metrics.py` executada por `make test`)

## Out of Scope (Deferred to Later Slices)

- Geração dos 5 gráficos estáticos PNG em 300 DPI (`src/charts.py` -> `reports/figures/`)
- Construção e execução automatizada do Jupyter Notebook executivo (`notebooks/02_analise_executiva.ipynb` e `notebooks/analise_orbitshop.ipynb`)
- Redação do Memo Executivo de 1 página (`reports/memo_orbitshop.md` e `reports/memo_orbitshop.pdf` com `<= 400` palavras) e do `README.md` final

## Subsequent Slice Plan

Cada fase subsequente adiciona uma fatia vertical sobre este esqueleto sem alterar suas decisões arquiteturais:

- Phase 2: Visualizações estáticas em 300 DPI (`src/charts.py`), Jupyter Notebook executivo executado (`nbconvert`), Memo Executivo de 1 página (MD/PDF `<= 400` palavras) e `README.md` executivo validados via `make reproduce` e `make all`.
