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
    q3_df["receita_nao_cancelada"] = q3_df["receita_nao_cancelada"].fillna(0.0)

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


def metrics_q5_monthly(
    df_pedidos: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, int | float | str]]:
    """Compute Q5 monthly order evolution (2023-2024) and the Nov/2023 Black Friday spike."""
    q5_df = (
        df_pedidos.groupby("ano_mes", as_index=False)
        .agg(
            total_pedidos=("id", "count"),
            cancelados=("is_cancelado", "sum"),
            taxa_cancel_pct=("is_cancelado", lambda s: float(s.mean() * 100)),
            pct_com_cupom=("cupom_desconto", lambda s: float((s == "sim").mean() * 100)),
            receita_pedidos=("valor_total", "sum"),
            receita_pedidos_imputada=("valor_total_imputado", "sum"),
            receita_liquida=("soma_liquida_itens", "sum"),
            ped_site=("canal_venda", lambda s: int((s == "site").sum())),
            ped_app=("canal_venda", lambda s: int((s == "app").sum())),
            ped_mkt=("canal_venda", lambda s: int((s == "marketplace").sum())),
        )
        .sort_values("ano_mes")
        .reset_index(drop=True)
    )

    nov23_row = q5_df.loc[q5_df["ano_mes"] == "2023-11"].iloc[0]
    nov24_row = q5_df.loc[q5_df["ano_mes"] == "2024-11"].iloc[0]
    media_ex_nov23 = float(
        q5_df.loc[q5_df["ano_mes"] != "2023-11", "total_pedidos"].mean()
    )
    pedidos_nov23 = int(nov23_row["total_pedidos"])

    summary: dict[str, int | float | str] = {
        "pico_ano_mes": "2023-11",
        "pedidos_nov_2023": pedidos_nov23,
        "ped_site_nov_2023": int(nov23_row["ped_site"]),
        "ped_app_nov_2023": int(nov23_row["ped_app"]),
        "ped_mkt_nov_2023": int(nov23_row["ped_mkt"]),
        "pedidos_nov_2024": int(nov24_row["total_pedidos"]),
        "media_pedidos_ex_nov2023": media_ex_nov23,
        "multiplo_pico_vs_media": float(pedidos_nov23 / media_ex_nov23),
    }
    return q5_df, summary


def metrics_q7_suppliers(
    data: dict[str, pd.DataFrame],
    itens_full: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Compute Q7 supplier quality ratings, support ticket incidence, and Nov-Dec 2023 surge."""
    if itens_full is None:
        itens_full = enrich_items(data["Itens_Pedido"], data["Produtos"])

    produtos = data["Produtos"]
    pedidos = data["Pedidos"]
    avaliacoes = data["Avaliacoes"]
    tickets = data["Tickets_Suporte"].copy()

    aval_prod = avaliacoes.merge(
        produtos[["id", "fornecedor", "categoria"]],
        left_on="produto_id",
        right_on="id",
        how="left",
        suffixes=("", "_prod"),
    )
    aval_forn = (
        aval_prod.groupby("fornecedor", as_index=False)
        .agg(
            qtd_avaliacoes=("id", "count"),
            nota_media=("nota", "mean"),
            pct_notas_baixas_1_2=("nota", lambda s: float((s <= 2).mean() * 100)),
        )
    )

    itens_ped = itens_full.merge(
        pedidos[["id", "status", "data_pedido"]],
        left_on="pedido_id",
        right_on="id",
        how="left",
        suffixes=("", "_ped"),
    )
    vendas_forn = (
        itens_ped.groupby("fornecedor", as_index=False)
        .agg(
            itens_vendidos=("id", "count"),
            unidades=("quantidade", "sum"),
            receita_liquida=("subtotal_liquido", "sum"),
            taxa_itens_cancelados_pct=(
                "status",
                lambda s: float((s == "cancelado").mean() * 100),
            ),
        )
    )

    ped_forn_unique = itens_full[["pedido_id", "fornecedor"]].drop_duplicates()
    tickets_forn = tickets.merge(ped_forn_unique, on="pedido_id", how="inner")
    tkt_forn_agg = (
        tickets_forn.groupby("fornecedor", as_index=False)
        .agg(
            tickets_associados=("id", "count"),
            tickets_defeito_troca=(
                "categoria_problema",
                lambda s: int(s.isin(["produto_com_defeito", "troca"]).sum()),
            ),
        )
    )

    q7_forn = (
        vendas_forn.merge(aval_forn, on="fornecedor", how="left")
        .merge(tkt_forn_agg, on="fornecedor", how="left")
    )
    q7_forn["tickets_por_100_itens"] = (
        q7_forn["tickets_associados"] / q7_forn["itens_vendidos"] * 100.0
    )
    q7_forn = q7_forn.sort_values("nota_media", ascending=True).reset_index(drop=True)

    tickets["ano_mes"] = tickets["data_abertura"].dt.to_period("M").astype(str)
    tickets_mensal = tickets.pivot_table(
        index="ano_mes",
        columns="categoria_problema",
        values="id",
        aggfunc="count",
        fill_value=0,
    )
    tickets_mensal["TOTAL"] = tickets_mensal.sum(axis=1)

    tickets_forn["ano_mes"] = tickets_forn["data_abertura"].dt.to_period("M").astype(str)
    tickets_forn_mensal = tickets_forn.pivot_table(
        index="ano_mes",
        columns="fornecedor",
        values="id",
        aggfunc="count",
        fill_value=0,
    )

    delta_row = q7_forn.loc[q7_forn["fornecedor"] == "DeltaFornece ME"].iloc[0]
    peers_df = q7_forn.loc[q7_forn["fornecedor"] != "DeltaFornece ME"]

    summary: dict[str, Any] = {
        "outlier_fornecedor": "DeltaFornece ME",
        "delta_nota_media": float(delta_row["nota_media"]),
        "delta_pct_notas_1_2": float(delta_row["pct_notas_baixas_1_2"]),
        "delta_tickets_por_100_itens": float(delta_row["tickets_por_100_itens"]),
        "peers_min_nota_media": float(peers_df["nota_media"].min()),
        "peers_max_nota_media": float(peers_df["nota_media"].max()),
        "peers_min_tickets_por_100_itens": float(
            peers_df["tickets_por_100_itens"].min()
        ),
        "peers_max_tickets_por_100_itens": float(
            peers_df["tickets_por_100_itens"].max()
        ),
        "tickets_nov_2023": int(tickets_mensal.loc["2023-11", "TOTAL"]),
        "tickets_dez_2023": int(tickets_mensal.loc["2023-12", "TOTAL"]),
        "tickets_forn_mensal_df": tickets_forn_mensal,
    }
    return q7_forn, tickets_mensal, summary


def metrics_q8_recommendation(df_pedidos: pd.DataFrame) -> dict[str, float | int]:
    """Compute Q8 financial sizing for restructuring paid_search cancellation rate."""
    ps_mask = df_pedidos["canal_aquisicao"] == "paid_search"
    other_mask = ~ps_mask

    pedidos_ps = int(ps_mask.sum())
    cancelados_ps = int(df_pedidos.loc[ps_mask, "is_cancelado"].sum())
    taxa_ps_pct = float(cancelados_ps / pedidos_ps * 100.0)

    pedidos_outros = int(other_mask.sum())
    cancelados_outros = int(df_pedidos.loc[other_mask, "is_cancelado"].sum())
    taxa_outros_exata_pct = float(cancelados_outros / pedidos_outros * 100.0)
    taxa_benchmark_prd_pct = 11.9

    ticket_medio_ps = float(df_pedidos.loc[ps_mask, "valor_total"].mean())
    ticket_medio_ps_imputado = float(
        df_pedidos.loc[ps_mask, "valor_total_imputado"].mean()
    )

    pedidos_recuperados = float(
        pedidos_ps * (cancelados_ps / pedidos_ps - taxa_benchmark_prd_pct / 100.0)
    )
    pedidos_recuperados_exato = float(
        pedidos_ps * (cancelados_ps / pedidos_ps - cancelados_outros / pedidos_outros)
    )
    receita_bruta_recuperavel = float(pedidos_recuperados * ticket_medio_ps)

    return {
        "pedidos_paid_search": pedidos_ps,
        "cancelados_paid_search": cancelados_ps,
        "taxa_paid_search_pct": taxa_ps_pct,
        "taxa_benchmark_outros_canais_pct": taxa_outros_exata_pct,
        "taxa_benchmark_prd_pct": taxa_benchmark_prd_pct,
        "pedidos_recuperados": pedidos_recuperados,
        "pedidos_recuperados_exato": pedidos_recuperados_exato,
        "ticket_medio_paid_search": ticket_medio_ps,
        "ticket_medio_paid_search_imputado": ticket_medio_ps_imputado,
        "receita_bruta_recuperavel": receita_bruta_recuperavel,
    }


__all__ = [
    "build_orders_analytical_df",
    "enrich_items",
    "metrics_camila_vs_rogerio",
    "metrics_q2_status",
    "metrics_q3_categories",
    "metrics_q4_channels",
    "metrics_q5_monthly",
    "metrics_q7_suppliers",
    "metrics_q8_recommendation",
]
