"""Deterministic business metrics for OrbitShop Due Diligence Series C (Q1-Q8)."""

from __future__ import annotations

from typing import Any

import pandas as pd
from scipy import stats

from src.audit import build_orders_analytical_df, enrich_items


def metrics_camila_vs_rogerio(df_pedidos: pd.DataFrame) -> dict[str, Any]:
    """Compute metrics for the Growth (Camila) vs. CFO (Rogerio) cancellation paradox."""
    total_pedidos = int(len(df_pedidos))
    cancelados_global = int(df_pedidos["is_cancelado"].sum())
    taxa_global_pct = float(cancelados_global / total_pedidos * 100)

    anual = (
        df_pedidos.groupby("ano", as_index=False)
        .agg(
            total_pedidos=("id", "count"),
            cancelados=("is_cancelado", "sum"),
            taxa_cancel_pct=("is_cancelado", lambda s: float(s.mean() * 100)),
            nao_convertidos=("is_nao_convertido", "sum"),
            taxa_nao_conv_pct=("is_nao_convertido", lambda s: float(s.mean() * 100)),
        )
    )

    semestral = (
        df_pedidos.groupby("semestre", as_index=False)
        .agg(
            total_pedidos=("id", "count"),
            cancelados=("is_cancelado", "sum"),
            taxa_cancel_pct=("is_cancelado", lambda s: float(s.mean() * 100)),
        )
    )

    fin = df_pedidos[df_pedidos["status"].isin(["entregue", "cancelado"])]
    fin_anual = (
        fin.groupby("ano")["is_cancelado"]
        .agg(
            finalizados="count",
            cancelados="sum",
            taxa_cancel_sobre_finalizados=lambda s: float(s.mean() * 100),
        )
        .reset_index()
    )

    ano_canal = (
        df_pedidos.groupby(["ano", "canal_aquisicao"])["is_cancelado"]
        .agg(pedidos="count", cancelados="sum", taxa_pct=lambda s: float(s.mean() * 100))
        .unstack("ano")
    )

    row_2023 = anual.loc[anual["ano"] == 2023].iloc[0]
    row_2024 = anual.loc[anual["ano"] == 2024].iloc[0]

    return {
        "total_pedidos": total_pedidos,
        "cancelados_global": cancelados_global,
        "taxa_cancel_global_pct": taxa_global_pct,
        "pedidos_2023": int(row_2023["total_pedidos"]),
        "cancelados_2023": int(row_2023["cancelados"]),
        "taxa_cancel_2023_pct": float(row_2023["taxa_cancel_pct"]),
        "pedidos_2024": int(row_2024["total_pedidos"]),
        "cancelados_2024": int(row_2024["cancelados"]),
        "taxa_cancel_2024_pct": float(row_2024["taxa_cancel_pct"]),
        "anual_df": anual,
        "semestral_df": semestral,
        "finalizados_anual_df": fin_anual,
        "ano_canal_df": ano_canal,
    }


def metrics_q2_status(df_pedidos: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Compute Q2 order status distribution and official revenue/ticket metrics."""
    total_pedidos = int(len(df_pedidos))
    q2_df = (
        df_pedidos.groupby("status", as_index=False)
        .agg(
            qtd_pedidos=("id", "count"),
            receita_pedidos=("valor_total", "sum"),
            ticket_medio_pedidos=("valor_total", "mean"),
            receita_pedidos_imputada=("valor_total_imputado", "sum"),
            ticket_medio_imputado=("valor_total_imputado", "mean"),
            receita_itens_liquida=("soma_liquida_itens", "sum"),
            ticket_medio_itens=("soma_liquida_itens", "mean"),
        )
    )
    q2_df["pct_pedidos"] = q2_df["qtd_pedidos"] / total_pedidos * 100.0
    q2_df = q2_df.sort_values("qtd_pedidos", ascending=False).reset_index(drop=True)

    status_map = q2_df.set_index("status").to_dict(orient="index")
    em_transito_2023 = int(
        ((df_pedidos["status"] == "em_transito") & (df_pedidos["ano"] == 2023)).sum()
    )
    em_transito_2024 = int(
        ((df_pedidos["status"] == "em_transito") & (df_pedidos["ano"] == 2024)).sum()
    )

    nao_conv_mask = df_pedidos["status"].isin(["cancelado", "devolvido"])
    nao_convertidos_qtd = int(nao_conv_mask.sum())
    nao_convertidos_pct = float(nao_convertidos_qtd / total_pedidos * 100.0)
    receita_nao_convertida = float(df_pedidos.loc[nao_conv_mask, "valor_total"].sum())
    receita_nao_convertida_imputada = float(
        df_pedidos.loc[nao_conv_mask, "valor_total_imputado"].sum()
    )

    summary: dict[str, Any] = {
        "entregue_qtd": int(status_map["entregue"]["qtd_pedidos"]),
        "entregue_pct": float(status_map["entregue"]["pct_pedidos"]),
        "entregue_receita": float(status_map["entregue"]["receita_pedidos"]),
        "entregue_ticket_medio": float(status_map["entregue"]["ticket_medio_pedidos"]),
        "cancelado_qtd": int(status_map["cancelado"]["qtd_pedidos"]),
        "cancelado_pct": float(status_map["cancelado"]["pct_pedidos"]),
        "cancelado_receita": float(status_map["cancelado"]["receita_pedidos"]),
        "cancelado_ticket_medio": float(status_map["cancelado"]["ticket_medio_pedidos"]),
        "em_transito_qtd": int(status_map["em_transito"]["qtd_pedidos"]),
        "em_transito_pct": float(status_map["em_transito"]["pct_pedidos"]),
        "em_transito_receita": float(status_map["em_transito"]["receita_pedidos"]),
        "em_transito_ticket_medio": float(status_map["em_transito"]["ticket_medio_pedidos"]),
        "em_transito_2023": em_transito_2023,
        "em_transito_2024": em_transito_2024,
        "devolvido_qtd": int(status_map["devolvido"]["qtd_pedidos"]),
        "devolvido_pct": float(status_map["devolvido"]["pct_pedidos"]),
        "devolvido_receita": float(status_map["devolvido"]["receita_pedidos"]),
        "devolvido_ticket_medio": float(status_map["devolvido"]["ticket_medio_pedidos"]),
        "nao_convertidos_qtd": nao_convertidos_qtd,
        "nao_convertidos_pct": nao_convertidos_pct,
        "receita_nao_convertida": receita_nao_convertida,
        "receita_nao_convertida_imputada": receita_nao_convertida_imputada,
    }
    return q2_df, summary


def metrics_q3_categories(itens_full: pd.DataFrame, pedidos: pd.DataFrame) -> pd.DataFrame:
    """Compute Q3 category ranking by physical volume vs. relative net item revenue."""
    itens_ped = itens_full.merge(
        pedidos[["id", "status"]],
        left_on="pedido_id",
        right_on="id",
        how="left",
        suffixes=("", "_ped"),
    )
    nao_cancel_mask = itens_ped["status"] != "cancelado"
    receita_nao_cancelada = (
        itens_ped[nao_cancel_mask]
        .groupby("categoria")["subtotal_liquido"]
        .sum()
        .rename("receita_nao_cancelada")
    )

    q3_df = (
        itens_ped.groupby("categoria", as_index=False)
        .agg(
            unidades_vendidas=("quantidade", "sum"),
            linhas_item=("id", "count"),
            receita_liquida=("subtotal_liquido", "sum"),
            preco_medio_praticado=("preco_praticado", "mean"),
            preco_catalogo_medio=("preco_unitario", "mean"),
            desconto_medio=("desc_efetivo", "mean"),
            lucro_total=("lucro_item", "sum"),
        )
        .merge(receita_nao_cancelada, on="categoria", how="left")
    )

    q3_df["ticket_liquido_por_unidade"] = (
        q3_df["receita_liquida"] / q3_df["unidades_vendidas"]
    )
    q3_df["margem_pct"] = q3_df["lucro_total"] / q3_df["receita_liquida"] * 100.0
    q3_df["rank_receita"] = (
        q3_df["receita_liquida"].rank(ascending=False, method="min").astype(int)
    )
    q3_df["rank_volume"] = (
        q3_df["unidades_vendidas"].rank(ascending=False, method="min").astype(int)
    )
    q3_df = q3_df.sort_values("receita_liquida", ascending=False).reset_index(drop=True)
    return q3_df


def metrics_q4_channels(
    df_pedidos: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, float | int]]:
    """Compute Q4 acquisition channel cancellation rates, tickets, and chi-square test."""
    q4_df = (
        df_pedidos.groupby("canal_aquisicao", as_index=False)
        .agg(
            clientes_unicos=("cliente_id", "nunique"),
            pedidos=("id", "count"),
            cancelados=("is_cancelado", "sum"),
            taxa_cancel_pct=("is_cancelado", lambda s: float(s.mean() * 100)),
            nao_convertidos=("is_nao_convertido", "sum"),
            taxa_nao_conv_pct=("is_nao_convertido", lambda s: float(s.mean() * 100)),
            ticket_medio_pedidos=("valor_total", "mean"),
            ticket_medio_imputado=("valor_total_imputado", "mean"),
            ticket_medio_itens=("soma_liquida_itens", "mean"),
            pct_b2b=("segmento", lambda s: float((s == "B2B").mean() * 100)),
        )
        .sort_values("taxa_cancel_pct", ascending=False)
        .reset_index(drop=True)
    )

    ct = pd.crosstab(df_pedidos["canal_aquisicao"], df_pedidos["is_cancelado"])
    chi2, p_val, dof, _ = stats.chi2_contingency(ct)

    by_channel = q4_df.set_index("canal_aquisicao").to_dict(orient="index")
    summary: dict[str, float | int] = {
        "paid_search_pedidos": int(by_channel["paid_search"]["pedidos"]),
        "paid_search_cancelados": int(by_channel["paid_search"]["cancelados"]),
        "paid_search_taxa_cancel_pct": float(by_channel["paid_search"]["taxa_cancel_pct"]),
        "paid_search_ticket_medio": float(
            by_channel["paid_search"]["ticket_medio_pedidos"]
        ),
        "indicacao_taxa_cancel_pct": float(by_channel["indicação"]["taxa_cancel_pct"]),
        "organico_taxa_cancel_pct": float(by_channel["orgânico"]["taxa_cancel_pct"]),
        "redes_sociais_taxa_cancel_pct": float(
            by_channel["redes_sociais"]["taxa_cancel_pct"]
        ),
        "chi2": float(chi2),
        "p_value": float(p_val),
        "dof": int(dof),
    }
    return q4_df, summary


__all__ = [
    "build_orders_analytical_df",
    "enrich_items",
    "metrics_camila_vs_rogerio",
    "metrics_q2_status",
    "metrics_q3_categories",
    "metrics_q4_channels",
]
