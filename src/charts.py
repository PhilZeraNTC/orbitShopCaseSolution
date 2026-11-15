"""Static 300 DPI executive chart generation and 1-page Memo PDF rendering."""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.audit import (
    audit_q6_by_segment,
    build_orders_analytical_df,
    enrich_items,
    reconcile_orders_vs_items,
)
from src.loader import PROJECT_ROOT, load_orbitshop_data
from src.metrics import (
    metrics_q2_status,
    metrics_q4_channels,
    metrics_q5_monthly,
    metrics_q7_suppliers,
)

FIGURES_DIR: Path = PROJECT_ROOT / "reports" / "figures"

# Corporate palette (Peers Consulting / Executive Dark Navy & Alert Red)
NAVY = "#1B365D"
SLATE = "#4B6584"
TEAL = "#20BF6B"
AMBER = "#F7B731"
CORAL = "#EB3B5A"
RED = "#D63031"
LIGHT_GRAY = "#DFE4EA"


def _apply_style() -> None:
    """Configure global matplotlib/seaborn executive styling."""
    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "axes.edgecolor": "#CCCCCC",
            "figure.titlesize": 14,
            "figure.titleweight": "bold",
            "savefig.dpi": 300,
        }
    )


def plot_q2_status(
    df_pedidos: pd.DataFrame, output_dir: Path = FIGURES_DIR
) -> Path:
    """Plot Q2 order status distribution and non-converted revenue impact (300 DPI)."""
    _apply_style()
    output_dir.mkdir(parents=True, exist_ok=True)
    q2_df, summary = metrics_q2_status(df_pedidos)

    label_map = {
        "entregue": "Entregue",
        "cancelado": "Cancelado",
        "em_transito": "Em Trânsito\n(788 de 2023)",
        "devolvido": "Devolvido",
    }
    color_map = {
        "entregue": NAVY,
        "cancelado": RED,
        "em_transito": AMBER,
        "devolvido": CORAL,
    }
    labels = [label_map.get(s, s) for s in q2_df["status"]]
    colors = [color_map.get(s, SLATE) for s in q2_df["status"]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.5))
    fig.suptitle(
        "Q2 — Funil de Status de Pedidos e Perda de Conversão (2023–2024)",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )

    # Panel A: Order volume and share
    bars1 = ax1.barh(labels[::-1], q2_df["qtd_pedidos"][::-1], color=colors[::-1], height=0.6)
    ax1.set_title("A. Volume de Pedidos por Status (Total: 15.000)")
    ax1.set_xlabel("Quantidade de Pedidos")
    ax1.set_xlim(0, 12000)
    for bar, (_, row) in zip(bars1, q2_df.iloc[::-1].iterrows()):
        w = bar.get_width()
        ax1.text(
            w + 180,
            bar.get_y() + bar.get_height() / 2,
            f"{int(row['qtd_pedidos']):,} ({row['pct_pedidos']:.2f}%)".replace(",", "."),
            va="center",
            fontsize=9.5,
            fontweight="bold",
        )

    # Panel B: Official Revenue (Pedidos.valor_total) in R$ Millions
    rev_m = q2_df["receita_pedidos"] / 1e6
    bars2 = ax2.barh(labels[::-1], rev_m[::-1], color=colors[::-1], height=0.6)
    nao_conv_rev_m = summary["receita_nao_convertida"] / 1e6
    sub_b = (
        f"({summary['nao_convertidos_pct']:.2f}% | R$ {nao_conv_rev_m:.2f}M)".replace(",", ".")
    )
    ax2.set_title(
        "B. Receita Oficial por Status (Pedidos.valor_total — R$ Milhões)\n"
        f"Não Convertidos (Cancelado + Devolvido): {summary['nao_convertidos_qtd']:,} ped. "
        + sub_b
    )
    ax2.set_xlabel("Receita Bruta (R$ Milhões)")
    ax2.set_xlim(0, 31)
    for bar, (_, row) in zip(bars2, q2_df.iloc[::-1].iterrows()):
        w = bar.get_width()
        rev_label = (
            f"R$ {row['receita_pedidos']/1e6:.2f}M\n"
            f"(TM: R$ {row['ticket_medio_pedidos']:,.0f})"
        ).replace(",", ".")
        ax2.text(
            w + 0.4,
            bar.get_y() + bar.get_height() / 2,
            rev_label,
            va="center",
            fontsize=9,
            fontweight="bold",
        )

    sns.despine(top=True, right=True)
    fig.tight_layout()
    out_path = output_dir / "q2_status_pedidos.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_q6_reconciliation(
    rec: pd.DataFrame, clientes: pd.DataFrame, output_dir: Path = FIGURES_DIR
) -> Path:
    """Plot Q6 financial reconciliation and B2B vs. B2C average ticket (300 DPI)."""
    _apply_style()
    output_dir.mkdir(parents=True, exist_ok=True)
    _, seg = audit_q6_by_segment(rec, clientes)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.5))
    fig.suptitle(
        "Q6 — Auditoria de Fonte da Verdade Financeira: Pedidos.valor_total vs. Itens_Pedido",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )

    # Panel A: B2B vs B2C average ticket comparison
    x = np.arange(2)
    width = 0.35
    b2b_b2c_pedidos = [seg["b2b_media_valor_total"], seg["b2c_media_valor_total"]]
    b2b_b2c_itens = [seg["b2b_media_itens"], seg["b2c_media_itens"]]

    rects1 = ax1.bar(
        x - width / 2,
        b2b_b2c_pedidos,
        width,
        label="Pedidos.valor_total (Fonte Oficial)",
        color=NAVY,
    )
    rects2 = ax1.bar(
        x + width / 2,
        b2b_b2c_itens,
        width,
        label="Soma Líquida Itens_Pedido (Distorcido)",
        color=CORAL,
    )
    ax1.set_title(
        f"A. Ticket Médio por Segmento: B2B = {seg['ratio_b2b_b2c']:.2f}x B2C em Pedidos\n"
        f"(vs. {seg['ratio_itens_b2b_b2c']:.2f}x em Itens_Pedido — r = -0,01)"
    )
    ax1.set_xticks(x)
    ax1.set_xticklabels(["B2B (3.014 pedidos)", "B2C (11.986 pedidos)"], fontweight="bold")
    ax1.set_ylabel("Ticket Médio (R$)")
    ax1.set_ylim(0, 13500)
    ax1.legend(loc="upper right", frameon=True)

    for rect in rects1:
        h = rect.get_height()
        ax1.text(
            rect.get_x() + rect.get_width() / 2,
            h + 250,
            f"R$ {h:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            ha="center",
            fontsize=9.5,
            fontweight="bold",
            color=NAVY,
        )
    for rect in rects2:
        h = rect.get_height()
        ax1.text(
            rect.get_x() + rect.get_width() / 2,
            h + 250,
            f"R$ {h:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            ha="center",
            fontsize=9.5,
            fontweight="bold",
            color=RED,
        )

    # Panel B: Aggregate total discrepancy
    totais_m = [
        rec["valor_total"].sum() / 1e6,
        rec["soma_liquida_itens"].sum() / 1e6,
    ]
    bars2 = ax2.bar(
        ["Pedidos.valor_total\n(14.921 válidos)", "Itens_Pedido Líquido\n(36.740 itens)"],
        totais_m,
        color=[NAVY, RED],
        width=0.5,
    )
    ax2.set_title(
        "B. Divergência Agregada Total (0 de 14.921 pedidos conciliam ±R$ 0,05)\n"
        "Diferença: -R$ 127,46 Milhões | 21.243 descontos sem cupom | 2.574 abaixo do custo"
    )
    ax2.set_ylabel("Volume Financeiro Acumulado (R$ Milhões)")
    ax2.set_ylim(0, 195)
    for bar in bars2:
        h = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            h + 3.5,
            f"R$ {h:.2f}M".replace(".", ","),
            ha="center",
            fontsize=11,
            fontweight="bold",
        )

    sns.despine(top=True, right=True)
    fig.tight_layout()
    out_path = output_dir / "q6_reconciliacao_b2b_b2c.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_q4_channels(
    df_pedidos: pd.DataFrame, output_dir: Path = FIGURES_DIR
) -> Path:
    """Plot Q4 cancellation rate and average ticket by acquisition channel (300 DPI)."""
    _apply_style()
    output_dir.mkdir(parents=True, exist_ok=True)
    q4_df, summary = metrics_q4_channels(df_pedidos)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.2))
    fig.suptitle(
        "Q4 & Q8 — Auditoria de Canais de Aquisição: Anomalia Crítica em Paid Search",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )

    colors = [
        RED if c == "paid_search" else NAVY for c in q4_df["canal_aquisicao"]
    ]
    bars1 = ax1.bar(
        q4_df["canal_aquisicao"], q4_df["taxa_cancel_pct"], color=colors, width=0.55
    )
    ax1.axhline(
        11.94,
        color=TEAL,
        linestyle="--",
        linewidth=1.8,
        label="Benchmark Demais Canais (11,9%)",
    )
    ax1.set_title(
        f"A. Taxa de Cancelamento por Canal (Chi² = {summary['chi2']:.2f}, p < 10⁻¹⁵⁸)\n"
        "Paid Search cancela 2,6x mais que os demais canais"
    )
    ax1.set_ylabel("Taxa de Cancelamento (%)")
    ax1.set_ylim(0, 37)
    ax1.legend(loc="upper right", frameon=True)
    for bar, (_, row) in zip(bars1, q4_df.iterrows()):
        h = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            h + 0.8,
            f"{h:.2f}%\n({int(row['cancelados'])}/{int(row['pedidos'])})",
            ha="center",
            fontsize=9.5,
            fontweight="bold",
        )

    bars2 = ax2.bar(
        q4_df["canal_aquisicao"],
        q4_df["ticket_medio_pedidos"],
        color=SLATE,
        width=0.55,
    )
    ax2.set_title(
        "B. Ticket Médio Oficial (Pedidos.valor_total) por Canal\n"
        "Ticket uniforme (~R$ 2.521 a R$ 2.657) — tráfego pago não traz maior valor"
    )
    ax2.set_ylabel("Ticket Médio (R$)")
    ax2.set_ylim(0, 3200)
    for bar in bars2:
        h = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            h + 55,
            f"R$ {h:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            ha="center",
            fontsize=9.5,
            fontweight="bold",
        )

    sns.despine(top=True, right=True)
    fig.tight_layout()
    out_path = output_dir / "q4_cancelamento_canais.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_q5_monthly(
    df_pedidos: pd.DataFrame, output_dir: Path = FIGURES_DIR
) -> Path:
    """Plot Q5 monthly order evolution (2023-2024) and Nov/2023 channel symmetry (300 DPI)."""
    _apply_style()
    output_dir.mkdir(parents=True, exist_ok=True)
    q5_df, summary = metrics_q5_monthly(df_pedidos)

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(14.5, 5.5), gridspec_kw={"width_ratios": [2.2, 1]}
    )
    fig.suptitle(
        "Q5 — Evolução Mensal de Pedidos (2023–2024) e Anomalia Isolada de Novembro/2023",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )

    bar_colors = [
        RED if m == "2023-11" else (AMBER if m == "2024-11" else NAVY)
        for m in q5_df["ano_mes"]
    ]
    ax1.bar(q5_df["ano_mes"], q5_df["total_pedidos"], color=bar_colors, width=0.7)
    media_ex = float(summary["media_pedidos_ex_nov2023"])
    ax1.axhline(
        media_ex,
        color=TEAL,
        linestyle="--",
        linewidth=1.8,
        label=f"Média ex-Nov/23: {media_ex:.0f} ped./mês",
    )
    ax1.set_title(
        "A. Série Histórica Mensal: Pico em 2023-11 (2.317 ped. = 4,2x a média) "
        "vs. 2024-11 (585 ped.)"
    )
    ax1.set_ylabel("Total de Pedidos / Mês")
    ax1.set_ylim(0, 2650)
    ax1.tick_params(axis="x", rotation=45)
    ax1.legend(loc="upper right", frameon=True)

    nov23_idx = int(q5_df.index[q5_df["ano_mes"] == "2023-11"][0])
    nov24_idx = int(q5_df.index[q5_df["ano_mes"] == "2024-11"][0])
    ax1.annotate(
        "2023-11: 2.317 ped.\n(4,2x a média)",
        xy=(nov23_idx, 2317),
        xytext=(nov23_idx - 4.5, 2400),
        arrowprops={"arrowstyle": "->", "color": RED, "lw": 1.5},
        fontsize=9.5,
        fontweight="bold",
        color=RED,
    )
    ax1.annotate(
        "2024-11: 585 ped.\n(Sem repetição)",
        xy=(nov24_idx, 585),
        xytext=(nov24_idx - 4.5, 1150),
        arrowprops={"arrowstyle": "->", "color": "#B33939", "lw": 1.5},
        fontsize=9,
        fontweight="bold",
        color="#B33939",
    )

    # Panel B: Symmetric channel distribution in 2023-11
    canais_venda = ["App", "Site", "Marketplace"]
    valores_nov23 = [
        int(summary["ped_app_nov_2023"]),
        int(summary["ped_site_nov_2023"]),
        int(summary["ped_mkt_nov_2023"]),
    ]
    bars2 = ax2.bar(canais_venda, valores_nov23, color=[NAVY, SLATE, TEAL], width=0.55)
    ax2.set_title("B. Simetria de Canais em Nov/2023\n(2.317 Pedidos distribuídos ~1/3 cada)")
    ax2.set_ylabel("Pedidos em 2023-11")
    ax2.set_ylim(0, 950)
    for bar in bars2:
        h = bar.get_height()
        pct = h / 2317 * 100
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            h + 20,
            f"{h}\n({pct:.1f}%)",
            ha="center",
            fontsize=9.5,
            fontweight="bold",
        )

    sns.despine(top=True, right=True)
    fig.tight_layout()
    out_path = output_dir / "q5_serie_mensal_2023_2024.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_q7_suppliers(
    data: dict[str, pd.DataFrame],
    itens_full: pd.DataFrame | None = None,
    output_dir: Path = FIGURES_DIR,
) -> Path:
    """Plot Q7 supplier quality vs. support ticket incidence and Nov-Dec 2023 surge (300 DPI)."""
    _apply_style()
    output_dir.mkdir(parents=True, exist_ok=True)
    q7_forn, tickets_mensal, summary = metrics_q7_suppliers(data, itens_full)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.0, 5.5))
    fig.suptitle(
        "Q7 — Qualidade de Fornecedores (Outlier DeltaFornece ME) vs. Sazonalidade de Tickets",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )

    # Panel A: Nota Média vs Tickets por 100 itens
    for _, row in q7_forn.iterrows():
        is_delta = row["fornecedor"] == "DeltaFornece ME"
        ax1.scatter(
            row["nota_media"],
            row["tickets_por_100_itens"],
            s=180 if is_delta else 110,
            color=RED if is_delta else NAVY,
            alpha=0.9,
            edgecolors="black",
            zorder=5 if is_delta else 3,
        )
        if is_delta:
            ax1.annotate(
                f"DeltaFornece ME\nNota: {row['nota_media']:.2f} (59,9% notas 1-2)\n"
                f"Tickets/100 itens: {row['tickets_por_100_itens']:.2f}",
                xy=(row["nota_media"], row["tickets_por_100_itens"]),
                xytext=(row["nota_media"] + 0.18, row["tickets_por_100_itens"] - 1.2),
                arrowprops={"arrowstyle": "->", "color": RED, "lw": 1.5},
                fontsize=9.5,
                fontweight="bold",
                color=RED,
            )

    ax1.set_title(
        "A. Nota Média de Avaliação vs. Taxa de Tickets / 100 Itens\n"
        "(DeltaFornece ME é outlier de nota, mas taxa de tickets é homogênea: 22,16–24,85)"
    )
    ax1.set_xlabel("Nota Média de Avaliação (1 a 5 estrelas)")
    ax1.set_ylabel("Tickets de Suporte por 100 Itens Vendidos")
    ax1.set_xlim(2.0, 4.1)
    ax1.set_ylim(20.0, 27.0)

    # Panel B: Monthly support tickets evolution
    meses = list(tickets_mensal.index)
    totais = list(tickets_mensal["TOTAL"])
    tkt_colors = [
        RED if m in ("2023-11", "2023-12") else SLATE for m in meses
    ]
    ax2.bar(meses, totais, color=tkt_colors, width=0.7)
    ax2.set_title(
        f"B. Evolução Mensal de Tickets de Suporte (Total: 4.000)\n"
        f"Salto em Nov/23 ({summary['tickets_nov_2023']}) e Dez/23 ({summary['tickets_dez_2023']}) "
        "ocorreu nos 9 fornecedores (efeito Black Friday)"
    )
    ax2.set_ylabel("Total de Chamados Abertos / Mês")
    ax2.set_ylim(0, 450)
    ax2.tick_params(axis="x", rotation=45)

    sns.despine(top=True, right=True)
    fig.tight_layout()
    out_path = output_dir / "q7_fornecedores_qualidade_tickets.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


def render_memo_pdf(
    md_path: Path = PROJECT_ROOT / "reports" / "memo_orbitshop.md",
    pdf_path: Path = PROJECT_ROOT / "reports" / "memo_orbitshop.pdf",
) -> Path:
    """Render the 1-page Executive Memo Markdown into a clean 1-page A4 PDF."""
    if not md_path.exists():
        raise FileNotFoundError(f"Memo Markdown não encontrado em: {md_path}")

    raw_text = md_path.read_text(encoding="utf-8")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(8.27, 11.69))
    ax = fig.add_axes([0.06, 0.04, 0.88, 0.92])
    ax.axis("off")

    # Top executive banner bar
    ax.plot([0.0, 1.0], [0.965, 0.965], color=NAVY, linewidth=2.5, transform=ax.transAxes)

    y = 0.985
    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line:
            y -= 0.010
            continue
        if line.startswith("---"):
            ax.plot(
                [0.0, 1.0], [y, y], color="#CBD5E1", linewidth=0.8, transform=ax.transAxes
            )
            y -= 0.014
            continue

        # Clean markdown syntax for PDF typography
        clean = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
        clean = re.sub(r"`(.*?)`", r"\1", clean)
        clean = clean.replace(
            r"$\chi^2 = 734,42, p < 10^{-158}$",
            "chi2 = 734,42, p < 10^-158",
        )

        if clean.startswith("# "):
            title_txt = clean[2:].strip()
            ax.text(
                0.0,
                y,
                title_txt,
                fontsize=12.5,
                fontweight="bold",
                color=NAVY,
                va="top",
                transform=ax.transAxes,
            )
            y -= 0.032
        elif clean.startswith("### "):
            sec_txt = clean[4:].strip()
            y -= 0.006
            ax.text(
                0.0,
                y,
                sec_txt,
                fontsize=10.2,
                fontweight="bold",
                color=NAVY,
                va="top",
                transform=ax.transAxes,
            )
            y -= 0.022
        elif any(clean.startswith(p) for p in ("Para:", "De:", "Data:", "Assunto:")):
            ax.text(
                0.0,
                y,
                clean,
                fontsize=8.8,
                fontweight="bold",
                color="#334155",
                va="top",
                transform=ax.transAxes,
            )
            y -= 0.017
        else:
            is_bullet = clean.startswith("- ")
            width = 96 if not is_bullet else 92
            wrapped = textwrap.wrap(
                clean,
                width=width,
                subsequent_indent="   " if is_bullet else "",
            )
            for wline in wrapped:
                ax.text(
                    0.0,
                    y,
                    wline,
                    fontsize=8.6,
                    color="#1E293B",
                    va="top",
                    transform=ax.transAxes,
                )
                y -= 0.0155
            y -= 0.004

    fig.savefig(pdf_path, format="pdf")
    plt.close(fig)
    return pdf_path


def generate_all_charts(output_dir: Path = FIGURES_DIR) -> dict[str, Path]:
    """Load data and generate all 5 executive 300 DPI PNG charts plus the 1-page PDF memo."""
    data = load_orbitshop_data()
    itens_full = enrich_items(data["Itens_Pedido"], data["Produtos"])
    rec, _ = reconcile_orders_vs_items(data["Pedidos"], itens_full, data["Clientes"])
    df_pedidos = build_orders_analytical_df(data)

    results: dict[str, Path] = {
        "q2_status": plot_q2_status(df_pedidos, output_dir),
        "q6_reconciliation": plot_q6_reconciliation(rec, data["Clientes"], output_dir),
        "q4_channels": plot_q4_channels(df_pedidos, output_dir),
        "q5_monthly": plot_q5_monthly(df_pedidos, output_dir),
        "q7_suppliers": plot_q7_suppliers(data, itens_full, output_dir),
    }
    memo_md = PROJECT_ROOT / "reports" / "memo_orbitshop.md"
    if memo_md.exists():
        results["memo_pdf"] = render_memo_pdf(memo_md)
    return results


if __name__ == "__main__":
    paths = generate_all_charts()
    for key, path in paths.items():
        print(f"[charts] Generated {key}: {path}")
