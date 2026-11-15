"""Null auditing, commercial anomaly detection, and Q6 financial reconciliation."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.loader import EXPECTED_ROW_COUNTS


def audit_nulls(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Audit null counts and percentages for every column across the 6 tables."""
    rows: list[dict[str, str | int | float]] = []
    for table_name in EXPECTED_ROW_COUNTS:
        df = data[table_name]
        total_rows = int(len(df))
        for col in df.columns:
            n_nulls = int(df[col].isna().sum())
            pct_nulls = float(n_nulls / total_rows * 100) if total_rows > 0 else 0.0
            rows.append(
                {
                    "tabela": table_name,
                    "coluna": str(col),
                    "nulos": n_nulls,
                    "total_linhas": total_rows,
                    "pct_nulos": pct_nulls,
                }
            )
    return pd.DataFrame(rows)


def get_null_summary(data: dict[str, pd.DataFrame]) -> dict[str, dict[str, float | int]]:
    """Return a structured summary of null counts and percentages for key columns."""
    df_nulls = audit_nulls(data)
    table_totals = df_nulls.groupby("tabela", sort=False)["nulos"].sum().to_dict()

    def _col_stats(table: str, col: str) -> dict[str, float | int]:
        row = df_nulls[(df_nulls["tabela"] == table) & (df_nulls["coluna"] == col)].iloc[0]
        return {
            "nulos": int(row["nulos"]),
            "total_linhas": int(row["total_linhas"]),
            "pct_nulos": float(row["pct_nulos"]),
        }

    return {
        "Clientes": {"nulos": int(table_totals["Clientes"]), "pct_nulos": 0.0},
        "Produtos": {"nulos": int(table_totals["Produtos"]), "pct_nulos": 0.0},
        "Pedidos.valor_total": _col_stats("Pedidos", "valor_total"),
        "Itens_Pedido.desconto_aplicado": _col_stats("Itens_Pedido", "desconto_aplicado"),
        "Tickets_Suporte.data_resolucao": _col_stats("Tickets_Suporte", "data_resolucao"),
        "Avaliacoes.comentario": _col_stats("Avaliacoes", "comentario"),
    }


def enrich_items(itens: pd.DataFrame, produtos: pd.DataFrame) -> pd.DataFrame:
    """Enrich Itens_Pedido with catalog product attributes and item-level financials."""
    prod_cols = ["id", "nome", "categoria", "preco_unitario", "custo_unitario", "fornecedor"]
    itens_full = itens.merge(
        produtos[prod_cols],
        left_on="produto_id",
        right_on="id",
        how="left",
        suffixes=("", "_prod"),
    ).copy()

    itens_full["desc_efetivo"] = itens_full["desconto_aplicado"].fillna(0.0)
    itens_full["subtotal_bruto"] = itens_full["quantidade"] * itens_full["preco_praticado"]
    itens_full["subtotal_liquido"] = itens_full["subtotal_bruto"] * (
        1.0 - itens_full["desc_efetivo"]
    )
    itens_full["custo_total_item"] = itens_full["quantidade"] * itens_full["custo_unitario"]
    itens_full["lucro_item"] = itens_full["subtotal_liquido"] - itens_full["custo_total_item"]
    itens_full["ratio_preco"] = itens_full["preco_praticado"] / itens_full["preco_unitario"]
    return itens_full


def audit_commercial_rules(
    itens_full: pd.DataFrame, pedidos: pd.DataFrame
) -> dict[str, int | float]:
    """Audit catalog price divergence, negative margin items, and coupon contradictions."""
    diff_catalogo = ~np.isclose(
        itens_full["preco_praticado"], itens_full["preco_unitario"], atol=0.01
    )
    itens_cupom = itens_full.merge(
        pedidos[["id", "cupom_desconto"]],
        left_on="pedido_id",
        right_on="id",
        how="left",
        suffixes=("", "_ped"),
    )

    desc_sem_cupom = (itens_cupom["cupom_desconto"] == "não") & (
        itens_cupom["desc_efetivo"] > 0
    )
    cupom_sem_desc = (itens_cupom["cupom_desconto"] == "sim") & (
        itens_cupom["desc_efetivo"] == 0
    )

    return {
        "total_itens": int(len(itens_full)),
        "itens_preco_diferente_catalogo": int(diff_catalogo.sum()),
        "pct_preco_diferente_catalogo": float(diff_catalogo.mean() * 100),
        "itens_abaixo_custo": int((itens_full["lucro_item"] < 0).sum()),
        "pct_itens_abaixo_custo": float((itens_full["lucro_item"] < 0).mean() * 100),
        "desconto_sem_cupom": int(desc_sem_cupom.sum()),
        "cupom_sem_desconto": int(cupom_sem_desc.sum()),
    }


def reconcile_orders_vs_items(
    pedidos: pd.DataFrame,
    itens_full: pd.DataFrame,
    clientes: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, dict[str, int | float]]:
    """Reconcile Pedidos.valor_total against aggregated Itens_Pedido net and gross totals (Q6)."""
    agg_itens = (
        itens_full.groupby("pedido_id", as_index=False)
        .agg(
            qtd_itens=("id", "count"),
            unidades=("quantidade", "sum"),
            soma_bruta_itens=("subtotal_bruto", "sum"),
            soma_liquida_itens=("subtotal_liquido", "sum"),
            custo_pedido=("custo_total_item", "sum"),
            lucro_pedido=("lucro_item", "sum"),
            tem_desc_nulo=("desconto_aplicado", lambda s: bool(s.isna().any())),
        )
    )

    rec = pedidos.merge(agg_itens, left_on="id", right_on="pedido_id", how="left").copy()
    rec["diff_liquida"] = rec["valor_total"] - rec["soma_liquida_itens"]
    rec["diff_bruta"] = rec["valor_total"] - rec["soma_bruta_itens"]

    validos = rec.dropna(subset=["valor_total"])
    um_item_validos = validos[validos["qtd_itens"] == 1]

    soma_pedidos = float(rec["valor_total"].sum())
    soma_itens = float(rec["soma_liquida_itens"].sum())

    summary: dict[str, int | float] = {
        "total_pedidos": int(len(rec)),
        "pedidos_valor_total_nulo": int(rec["valor_total"].isna().sum()),
        "pedidos_validos": int(len(validos)),
        "conciliam_liquida": int(np.isclose(validos["diff_liquida"], 0.0, atol=0.05).sum()),
        "conciliam_bruta": int(np.isclose(validos["diff_bruta"], 0.0, atol=0.05).sum()),
        "pedidos_1_item": int(len(um_item_validos)),
        "conciliam_1_item": int(
            np.isclose(um_item_validos["diff_liquida"], 0.0, atol=0.05).sum()
        ),
        "soma_valor_total_pedidos": soma_pedidos,
        "soma_liquida_itens": soma_itens,
        "soma_liquida_itens_validos": float(validos["soma_liquida_itens"].sum()),
        "diferenca_agregada": float(soma_pedidos - soma_itens),
        "correlacao_global": float(validos["valor_total"].corr(validos["soma_liquida_itens"])),
    }
    return rec, summary


def audit_q6_by_segment(
    rec: pd.DataFrame, clientes: pd.DataFrame
) -> tuple[pd.DataFrame, dict[str, float | int]]:
    """Compare Pedidos.valor_total vs. Itens_Pedido net sum across B2B and B2C segments (Q6)."""
    if "segmento" in rec.columns:
        rec_cli = rec.copy()
    else:
        rec_cli = rec.merge(
            clientes[["id", "segmento", "canal_aquisicao"]],
            left_on="cliente_id",
            right_on="id",
            how="left",
            suffixes=("", "_cli"),
        )

    seg_df = (
        rec_cli.groupby("segmento", as_index=False)
        .agg(
            qtd_pedidos=("id", "count"),
            nulos_valor_total=("valor_total", lambda s: int(s.isna().sum())),
            media_valor_total_pedidos=("valor_total", "mean"),
            mediana_valor_total_pedidos=("valor_total", "median"),
            media_soma_liquida_itens=("soma_liquida_itens", "mean"),
            mediana_soma_liquida_itens=("soma_liquida_itens", "median"),
        )
    )

    corrs: dict[str, float] = {}
    for seg_name, grp in rec_cli.dropna(subset=["valor_total"]).groupby("segmento"):
        corrs[str(seg_name)] = float(grp["valor_total"].corr(grp["soma_liquida_itens"]))
    seg_df["correlacao"] = seg_df["segmento"].map(corrs)

    b2b_row = seg_df.loc[seg_df["segmento"] == "B2B"].iloc[0]
    b2c_row = seg_df.loc[seg_df["segmento"] == "B2C"].iloc[0]

    media_b2b = float(b2b_row["media_valor_total_pedidos"])
    media_b2c = float(b2c_row["media_valor_total_pedidos"])
    mediana_b2b = round(float(b2b_row["mediana_valor_total_pedidos"]) + 1e-9, 2)
    mediana_b2c = round(float(b2c_row["mediana_valor_total_pedidos"]) + 1e-9, 2)

    # Impute nulls by segment median
    median_map = {"B2B": mediana_b2b, "B2C": mediana_b2c}
    rec_cli["valor_total_imputado"] = rec_cli["valor_total"].fillna(
        rec_cli["segmento"].map(median_map)
    )
    media_b2b_imp = float(
        rec_cli.loc[rec_cli["segmento"] == "B2B", "valor_total_imputado"].mean()
    )
    media_b2c_imp = float(
        rec_cli.loc[rec_cli["segmento"] == "B2C", "valor_total_imputado"].mean()
    )

    summary: dict[str, float | int] = {
        "b2b_pedidos": int(b2b_row["qtd_pedidos"]),
        "b2c_pedidos": int(b2c_row["qtd_pedidos"]),
        "b2b_nulos_valor_total": int(b2b_row["nulos_valor_total"]),
        "b2c_nulos_valor_total": int(b2c_row["nulos_valor_total"]),
        "b2b_media_valor_total": media_b2b,
        "b2c_media_valor_total": media_b2c,
        "b2b_mediana_valor_total": mediana_b2b,
        "b2c_mediana_valor_total": mediana_b2c,
        "b2b_media_imputada": media_b2b_imp,
        "b2c_media_imputada": media_b2c_imp,
        "b2b_media_itens": float(b2b_row["media_soma_liquida_itens"]),
        "b2c_media_itens": float(b2c_row["media_soma_liquida_itens"]),
        "ratio_b2b_b2c": float(media_b2b / media_b2c),
        "ratio_b2b_b2c_imputado": float(media_b2b_imp / media_b2c_imp),
        "ratio_itens_b2b_b2c": float(
            b2b_row["media_soma_liquida_itens"] / b2c_row["media_soma_liquida_itens"]
        ),
        "correlacao_b2b": float(b2b_row["correlacao"]),
        "correlacao_b2c": float(b2c_row["correlacao"]),
    }
    return seg_df, summary


def build_orders_analytical_df(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build the master analytical orders DataFrame with segment median imputation for Q1-Q8."""
    itens_full = enrich_items(data["Itens_Pedido"], data["Produtos"])
    rec, _ = reconcile_orders_vs_items(data["Pedidos"], itens_full, data["Clientes"])

    df_pedidos = rec.merge(
        data["Clientes"][["id", "segmento", "canal_aquisicao"]],
        left_on="cliente_id",
        right_on="id",
        how="left",
        suffixes=("", "_cli"),
    ).copy()

    df_pedidos["ano"] = df_pedidos["data_pedido"].dt.year
    df_pedidos["ano_mes"] = df_pedidos["data_pedido"].dt.to_period("M").astype(str)
    df_pedidos["semestre"] = (
        df_pedidos["data_pedido"].dt.year.astype(str)
        + "-S"
        + np.where(df_pedidos["data_pedido"].dt.month <= 6, "1", "2")
    )
    df_pedidos["is_cancelado"] = df_pedidos["status"] == "cancelado"
    df_pedidos["is_nao_convertido"] = df_pedidos["status"].isin(["cancelado", "devolvido"])

    segment_medians = (
        df_pedidos.groupby("segmento")["valor_total"]
        .transform("median")
        .apply(lambda v: round(float(v) + 1e-9, 2))
    )
    df_pedidos["valor_total_imputado"] = df_pedidos["valor_total"].fillna(segment_medians)

    return df_pedidos
