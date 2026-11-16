"""Automated pytest suite verifying Ground Truth invariants for OrbitShop (Q1-Q8)."""

from __future__ import annotations

import json

import pandas as pd
import pytest
from PIL import Image

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
from src.metrics import (
    metrics_camila_vs_rogerio,
    metrics_q2_status,
    metrics_q3_categories,
    metrics_q4_channels,
    metrics_q5_monthly,
    metrics_q7_suppliers,
    metrics_q8_recommendation,
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


def test_paradox_and_q2_status(df_pedidos: pd.DataFrame) -> None:
    """Verify PRD Section 3.3 Camila vs. Rogerio cancellation paradox and Q2 order status."""
    cr = metrics_camila_vs_rogerio(df_pedidos)
    assert cr["total_pedidos"] == 15000
    assert cr["cancelados_global"] == 2537
    assert cr["taxa_cancel_global_pct"] == pytest.approx(16.91, abs=0.01)
    assert cr["pedidos_2023"] == 8386
    assert cr["cancelados_2023"] == 1407
    assert cr["taxa_cancel_2023_pct"] == pytest.approx(16.78, abs=0.01)
    assert cr["pedidos_2024"] == 6614
    assert cr["cancelados_2024"] == 1130
    assert cr["taxa_cancel_2024_pct"] == pytest.approx(17.08, abs=0.01)

    _, q2 = metrics_q2_status(df_pedidos)
    assert q2["entregue_qtd"] == 9959
    assert q2["entregue_pct"] == pytest.approx(66.39, abs=0.01)
    assert q2["cancelado_qtd"] == 2537
    assert q2["cancelado_pct"] == pytest.approx(16.91, abs=0.01)
    assert q2["em_transito_qtd"] == 1371
    assert q2["em_transito_pct"] == pytest.approx(9.14, abs=0.01)
    assert q2["em_transito_2023"] == 788
    assert q2["devolvido_qtd"] == 1133
    assert q2["devolvido_pct"] == pytest.approx(7.55, abs=0.01)
    assert q2["nao_convertidos_qtd"] == 3670
    assert q2["nao_convertidos_pct"] == pytest.approx(24.47, abs=0.01)
    assert q2["receita_nao_convertida"] == pytest.approx(9467259.31, abs=0.01)


def test_q3_categories(
    raw_data: dict[str, pd.DataFrame], itens_full: pd.DataFrame
) -> None:
    """Verify PRD Section 3.4 (Q3) volume vs. relative item revenue category rankings."""
    q3_df = metrics_q3_categories(itens_full, raw_data["Pedidos"])

    # Revenue rank (already sorted by receita_liquida desc)
    assert list(q3_df["categoria"]) == [
        "Eletrônicos",
        "Casa & Decoração",
        "Beleza & Saúde",
        "Esporte & Lazer",
        "Moda",
        "Livros & Papelaria",
        "Bebês & Crianças",
        "Alimentos & Bebidas",
    ]
    assert q3_df.loc[0, "receita_liquida"] == pytest.approx(30801235.39, abs=0.01)
    assert q3_df.loc[1, "receita_liquida"] == pytest.approx(24516724.17, abs=0.01)
    assert q3_df.loc[2, "receita_liquida"] == pytest.approx(23347196.82, abs=0.01)
    assert q3_df.loc[3, "receita_liquida"] == pytest.approx(20233855.75, abs=0.01)
    assert q3_df.loc[4, "receita_liquida"] == pytest.approx(19862985.25, abs=0.01)

    # Volume top 3
    vol_df = q3_df.sort_values("unidades_vendidas", ascending=False).reset_index(drop=True)
    assert list(vol_df["categoria"][:3]) == ["Eletrônicos", "Casa & Decoração", "Moda"]
    assert list(vol_df["unidades_vendidas"][:3]) == [18658, 17899, 15680]

    # Moda has lowest average practiced price (R$ 1,347.98)
    moda_price = float(
        q3_df.loc[q3_df["categoria"] == "Moda", "preco_medio_praticado"].iloc[0]
    )
    assert moda_price == pytest.approx(1347.98, abs=0.01)
    assert moda_price == float(q3_df["preco_medio_praticado"].min())


def test_q4_acquisition_channels(df_pedidos: pd.DataFrame) -> None:
    """Verify PRD Section 3.5 (Q4) acquisition channel cancellation rates and chi2 test."""
    q4_df, q4 = metrics_q4_channels(df_pedidos)
    assert q4["paid_search_pedidos"] == 3965
    assert q4["paid_search_cancelados"] == 1219
    assert q4["paid_search_taxa_cancel_pct"] == pytest.approx(30.74, abs=0.01)
    assert q4["indicacao_taxa_cancel_pct"] == pytest.approx(12.38, abs=0.01)
    assert q4["organico_taxa_cancel_pct"] == pytest.approx(11.78, abs=0.01)
    assert q4["redes_sociais_taxa_cancel_pct"] == pytest.approx(11.67, abs=0.01)
    assert q4["chi2"] == pytest.approx(734.42, abs=0.01)
    assert q4["p_value"] < 1e-150
    assert q4["paid_search_ticket_medio"] == pytest.approx(2553.51, abs=0.01)
    assert float(q4_df["ticket_medio_pedidos"].min()) == pytest.approx(2521.15, abs=0.01)
    assert float(q4_df["ticket_medio_pedidos"].max()) == pytest.approx(2657.17, abs=0.01)


def test_q5_monthly_evolution(df_pedidos: pd.DataFrame) -> None:
    """Verify PRD Section 3.6 (Q5) monthly evolution and Nov/2023 Black Friday spike."""
    q5_df, q5 = metrics_q5_monthly(df_pedidos)
    assert len(q5_df) == 24
    assert q5["pico_ano_mes"] == "2023-11"
    assert q5["pedidos_nov_2023"] == 2317
    assert q5["ped_site_nov_2023"] == 770
    assert q5["ped_app_nov_2023"] == 783
    assert q5["ped_mkt_nov_2023"] == 764
    assert q5["pedidos_nov_2024"] == 585
    assert round(float(q5["media_pedidos_ex_nov2023"])) == 551
    assert q5["multiplo_pico_vs_media"] == pytest.approx(4.20, abs=0.02)


def test_q7_suppliers_and_support(
    raw_data: dict[str, pd.DataFrame], itens_full: pd.DataFrame
) -> None:
    """Verify PRD Section 3.7 (Q7) DeltaFornece ME quality outlier and Nov-Dec 2023 tickets."""
    q7_forn, _, q7 = metrics_q7_suppliers(raw_data, itens_full)
    assert len(q7_forn) == 9
    assert q7["outlier_fornecedor"] == "DeltaFornece ME"
    assert q7["delta_nota_media"] == pytest.approx(2.30, abs=0.01)
    assert q7["delta_pct_notas_1_2"] == pytest.approx(59.90, abs=0.01)
    assert q7["delta_tickets_por_100_itens"] == pytest.approx(22.94, abs=0.01)
    assert q7["peers_min_nota_media"] == pytest.approx(3.62, abs=0.01)
    assert q7["peers_max_nota_media"] == pytest.approx(3.84, abs=0.01)
    assert q7["peers_min_tickets_por_100_itens"] == pytest.approx(22.16, abs=0.01)
    assert q7["peers_max_tickets_por_100_itens"] == pytest.approx(24.85, abs=0.01)
    assert q7["tickets_nov_2023"] == 375
    assert q7["tickets_dez_2023"] == 391


def test_q8_recommendation_sizing(df_pedidos: pd.DataFrame) -> None:
    """Verify PRD Section 3.8 (Q8) financial sizing of paid_search restructuring."""
    q8 = metrics_q8_recommendation(df_pedidos)
    assert q8["pedidos_paid_search"] == 3965
    assert q8["cancelados_paid_search"] == 1219
    assert q8["taxa_paid_search_pct"] == pytest.approx(30.74, abs=0.01)
    assert round(float(q8["pedidos_recuperados"])) == 747
    assert q8["ticket_medio_paid_search"] == pytest.approx(2553.51, abs=0.01)
    assert q8["receita_bruta_recuperavel"] / 1e6 == pytest.approx(1.91, abs=0.01)


def test_phase2_deliverables_and_memo_constraints() -> None:
    """Verify Phase 2 deliverables: 300 DPI PNG figures and executed notebooks."""
    figures = [
        "q2_status_pedidos.png",
        "q6_reconciliacao_b2b_b2c.png",
        "q4_cancelamento_canais.png",
        "q5_serie_mensal_2023_2024.png",
        "q7_fornecedores_qualidade_tickets.png",
    ]
    figures_dir = PROJECT_ROOT / "reports" / "figures"
    for fname in figures:
        fpath = figures_dir / fname
        assert fpath.exists(), f"Missing figure: {fpath}"
        assert fpath.stat().st_size > 30000
        dpi = Image.open(fpath).info.get("dpi", (0, 0))[0]
        assert round(dpi) == 300

    for nb_name in ("02_analise_executiva.ipynb", "analise_orbitshop.ipynb"):
        nb_path = PROJECT_ROOT / "notebooks" / nb_name
        assert nb_path.exists()
        nb_data = json.loads(nb_path.read_text(encoding="utf-8"))
        code_cells = [c for c in nb_data["cells"] if c["cell_type"] == "code"]
        assert len(code_cells) >= 8
        assert all(
            c.get("execution_count") is not None and len(c.get("outputs", [])) > 0
            for c in code_cells
        )


