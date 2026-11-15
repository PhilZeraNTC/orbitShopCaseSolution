"""Automated pytest suite verifying Ground Truth invariants for OrbitShop (Q1-Q8)."""

from __future__ import annotations

import pandas as pd
import pytest

from src.audit import (
    audit_commercial_rules,
    audit_nulls,
    audit_q6_by_segment,
    build_orders_analytical_df,
    enrich_items,
    get_null_summary,
    reconcile_orders_vs_items,
)
from src.loader import (
    DEFAULT_DATA_PATH,
    EXPECTED_ROW_COUNTS,
    PROJECT_ROOT,
    audit_primary_keys,
    audit_relational_integrity,
    load_orbitshop_data,
)


@pytest.fixture(scope="session")
def raw_data() -> dict[str, pd.DataFrame]:
    """Load the 6 typed transactional sheets once per test session."""
    return load_orbitshop_data()


@pytest.fixture(scope="session")
def itens_full(raw_data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Enrich Itens_Pedido with catalog product attributes once per session."""
    return enrich_items(raw_data["Itens_Pedido"], raw_data["Produtos"])


@pytest.fixture(scope="session")
def df_pedidos(raw_data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build the master analytical orders DataFrame once per session."""
    return build_orders_analytical_df(raw_data)


def test_raw_data_file_integrity() -> None:
    """Verify raw Excel dataset and historical EDA notebook exist and are non-empty."""
    eda_nb = PROJECT_ROOT / "notebooks" / "01_eda_auditoria_exploratoria.ipynb"
    assert DEFAULT_DATA_PATH.exists(), f"Missing dataset at {DEFAULT_DATA_PATH}"
    assert DEFAULT_DATA_PATH.stat().st_size > 1_000_000
    assert eda_nb.exists(), f"Missing historical EDA notebook at {eda_nb}"
    assert eda_nb.stat().st_size > 10_000


def test_row_counts_and_null_invariants(raw_data: dict[str, pd.DataFrame]) -> None:
    """Verify PRD Section 3.1 row counts and null invariants across all 6 tables."""
    actual_counts = {name: len(df) for name, df in raw_data.items()}
    assert actual_counts == EXPECTED_ROW_COUNTS
    assert actual_counts == {
        "Clientes": 3000,
        "Produtos": 200,
        "Pedidos": 15000,
        "Itens_Pedido": 36740,
        "Tickets_Suporte": 4000,
        "Avaliacoes": 8000,
    }

    null_df = audit_nulls(raw_data)
    assert not null_df.empty
    summary = get_null_summary(raw_data)

    assert summary["Clientes"]["nulos"] == 0
    assert summary["Produtos"]["nulos"] == 0

    assert summary["Pedidos.valor_total"]["nulos"] == 79
    assert summary["Pedidos.valor_total"]["pct_nulos"] == pytest.approx(0.53, abs=0.01)

    assert summary["Itens_Pedido.desconto_aplicado"]["nulos"] == 301
    assert summary["Itens_Pedido.desconto_aplicado"]["pct_nulos"] == pytest.approx(
        0.82, abs=0.01
    )

    assert summary["Tickets_Suporte.data_resolucao"]["nulos"] == 1653
    assert summary["Tickets_Suporte.data_resolucao"]["pct_nulos"] == pytest.approx(
        41.33, abs=0.01
    )

    assert summary["Avaliacoes.comentario"]["nulos"] == 1679
    assert summary["Avaliacoes.comentario"]["pct_nulos"] == pytest.approx(
        20.99, abs=0.01
    )


def test_relational_and_temporal_integrity(raw_data: dict[str, pd.DataFrame]) -> None:
    """Verify PRD Section 3.1 zero duplicate PKs, zero orphan FKs, and temporal consistency."""
    pk_df = audit_primary_keys(raw_data)
    assert int(pk_df["duplicatas_exatas"].sum()) == 0
    assert int(pk_df["ids_duplicados"].sum()) == 0
    assert int(pk_df["ids_nulos"].sum()) == 0

    rel = audit_relational_integrity(raw_data)
    assert len(rel) == 10
    for check_name, count in rel.items():
        assert count == 0, f"Integrity violation in {check_name}: {count}"


def test_commercial_anomalies(
    raw_data: dict[str, pd.DataFrame], itens_full: pd.DataFrame
) -> None:
    """Verify PRD Section 3.2 commercial anomalies in Itens_Pedido."""
    comm = audit_commercial_rules(itens_full, raw_data["Pedidos"])
    assert comm["total_itens"] == 36740
    assert comm["itens_preco_diferente_catalogo"] == 34148
    assert comm["pct_preco_diferente_catalogo"] == pytest.approx(92.95, abs=0.01)
    assert comm["itens_abaixo_custo"] == 2574
    assert comm["desconto_sem_cupom"] == 21243
    assert comm["cupom_sem_desconto"] == 304


def test_q6_financial_reconciliation(
    raw_data: dict[str, pd.DataFrame], itens_full: pd.DataFrame
) -> None:
    """Verify PRD Section 3.2 (Q6) financial reconciliation and B2B vs. B2C segmentation."""
    rec, summary = reconcile_orders_vs_items(
        raw_data["Pedidos"], itens_full, raw_data["Clientes"]
    )
    assert summary["total_pedidos"] == 15000
    assert summary["pedidos_valor_total_nulo"] == 79
    assert summary["pedidos_validos"] == 14921
    assert summary["conciliam_liquida"] == 0
    assert summary["conciliam_bruta"] == 0
    assert summary["pedidos_1_item"] == 4408
    assert summary["conciliam_1_item"] == 0
    assert summary["soma_valor_total_pedidos"] == pytest.approx(38418252.65, abs=0.01)
    assert summary["soma_liquida_itens"] == pytest.approx(165878066.67, abs=0.01)
    assert summary["diferenca_agregada"] == pytest.approx(-127459814.02, abs=0.01)
    assert summary["correlacao_global"] == pytest.approx(-0.01, abs=0.005)

    _, seg = audit_q6_by_segment(rec, raw_data["Clientes"])
    assert seg["b2b_pedidos"] == 3014
    assert seg["b2c_pedidos"] == 11986
    assert seg["b2b_nulos_valor_total"] == 13
    assert seg["b2c_nulos_valor_total"] == 66
    assert seg["b2b_mediana_valor_total"] == pytest.approx(7803.97, abs=0.01)
    assert seg["b2c_mediana_valor_total"] == pytest.approx(1255.37, abs=0.01)
    assert seg["b2b_media_valor_total"] == pytest.approx(7778.34, abs=0.01)
    assert seg["b2c_media_valor_total"] == pytest.approx(1264.72, abs=0.01)
    assert seg["ratio_b2b_b2c"] == pytest.approx(6.15, abs=0.01)
    assert seg["ratio_b2b_b2c_imputado"] == pytest.approx(6.15, abs=0.01)
