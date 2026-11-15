.PHONY: setup test reproduce all

setup:
	uv sync

test:
	uv run pytest -v

reproduce:
	@if [ -f src/charts.py ]; then uv run python -m src.charts; fi
	@if [ -f notebooks/02_analise_executiva.ipynb ]; then \
		uv run jupyter nbconvert --to notebook --execute --inplace notebooks/02_analise_executiva.ipynb && \
		cp notebooks/02_analise_executiva.ipynb notebooks/analise_orbitshop.ipynb; \
	fi
	$(MAKE) test

all:
	$(MAKE) setup && $(MAKE) reproduce

