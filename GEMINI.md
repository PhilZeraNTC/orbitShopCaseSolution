<!-- GSD:project-start source:PROJECT.md -->

## Project

**OrbitShop Due Diligence Series C (Case Peers Consulting & Technology)**

Um repositório Python auto-contido, determinístico e auditável que reproduz integralmente a análise de Due Diligence Series C da OrbitShop (questões Q1 a Q9), refatorando a investigação exploratória validada (`notebooks/01_eda_auditoria_exploratoria.ipynb`) em módulos testados (`src/loader.py`, `src/audit.py`, `src/metrics.py`, `src/charts.py`). Entrega suíte de testes unitários (`pytest`) validando os invariantes numéricos de Ground Truth, gráficos estáticos em alta resolução (300 DPI), Jupyter Notebook executivo executado (`notebooks/02_analise_executiva.ipynb` / `notebooks/analise_orbitshop.ipynb`), Memo Executivo de 1 página (`reports/memo_orbitshop.md` e `reports/memo_orbitshop.pdf`, máx. 400 palavras) e `README.md` executivo com execução automatizada via `Makefile`.

**Core Value:** Reprodutibilidade determinística e auditável de 100% dos números-chave e invariantes de negócio da Due Diligence da OrbitShop (Q1 a Q9) a partir da base original `Base_Dados_OrbitShop.xlsx`, validada por testes automatizados (`pytest`) e executável em 1 comando (`make reproduce` / `make all`).

### Constraints

- **Tech Stack**: Python com `uv` (`pyproject.toml` + `uv.lock`) e `requirements.txt` espelhado — garante reprodutibilidade moderna e compatibilidade universal com `pip`
- **Dependencies**: Apenas `pandas`, `openpyxl`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `jupyter`, `nbconvert`, `pytest`, `ruff` (mais ferramenta leve para geração do PDF do memo se necessário) — sem `plotly`, `skimpy` ou `missingno`
- **Determinismo Numérico**: Funções em `src/` devem reproduzir exatamente os valores validados no Ground Truth e em `notebooks/01_eda_auditoria_exploratoria.ipynb`
- **Qualidade Visual**: Gráficos estáticos exportados em PNG a 300 DPI em `reports/figures/`
- **Restrição Editorial**: Memo executivo (`reports/memo_orbitshop.md` e `reports/memo_orbitshop.pdf`) deve ter 1 página e no máximo 400 palavras
- **Estrutura de Fases**: Divisão em 2 fases conforme definido pelo usuário: Fase 1 (Core & Testes) e Fase 2 (Notebook & Gráficos & Entregáveis Executivos)

<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->

## Technology Stack

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.agents/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-fast` for a trivial task inline, with no subagents and no PLAN.md
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
