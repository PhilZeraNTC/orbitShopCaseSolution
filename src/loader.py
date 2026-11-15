"""Data loading, schema typing, and relational integrity auditing for OrbitShop."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH: Path = PROJECT_ROOT / "data" / "Base_Dados_OrbitShop.xlsx"

EXPECTED_ROW_COUNTS: dict[str, int] = {
    "Clientes": 3000,
    "Produtos": 200,
    "Pedidos": 15000,
    "Itens_Pedido": 36740,
    "Tickets_Suporte": 4000,
    "Avaliacoes": 8000,
}

DATE_COLUMNS: dict[str, list[str]] = {
    "Clientes": ["data_cadastro"],
    "Pedidos": ["data_pedido"],
    "Tickets_Suporte": ["data_abertura", "data_resolucao"],
    "Avaliacoes": ["data_avaliacao"],
}


def _resolve_data_path(path: Path | str | None = None) -> Path:
    """Resolve the OrbitShop Excel file path, falling back to root if needed."""
    if path is not None:
        resolved = Path(path)
        if not resolved.exists():
            raise FileNotFoundError(f"Arquivo de dados não encontrado em: {resolved}")
        return resolved
    if DEFAULT_DATA_PATH.exists():
        return DEFAULT_DATA_PATH
    fallback = PROJECT_ROOT / "Base_Dados_OrbitShop.xlsx"
    if fallback.exists():
        return fallback
    raise FileNotFoundError(f"Arquivo de dados não encontrado em: {DEFAULT_DATA_PATH}")


def load_raw_sheets(path: Path | str | None = None) -> dict[str, pd.DataFrame]:
    """Load all sheets (including 'Leia-me') from Base_Dados_OrbitShop.xlsx."""
    excel_path = _resolve_data_path(path)
    return pd.read_excel(excel_path, sheet_name=None, engine="openpyxl")


def load_orbitshop_data(path: Path | str | None = None) -> dict[str, pd.DataFrame]:
    """Load and type the 6 transactional sheets of Base_Dados_OrbitShop.xlsx."""
    raw_sheets = load_raw_sheets(path)
    data: dict[str, pd.DataFrame] = {}

    for sheet_name in EXPECTED_ROW_COUNTS:
        if sheet_name not in raw_sheets:
            raise KeyError(f"Aba obrigatória ausente na planilha: {sheet_name}")
        df = raw_sheets[sheet_name].copy()
        for col in DATE_COLUMNS.get(sheet_name, []):
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        data[sheet_name] = df

    return data


def audit_primary_keys(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Audit row/column counts, exact duplicates, duplicate IDs, and null IDs across all 6 tables."""
    rows: list[dict[str, int | str]] = []
    for table_name in EXPECTED_ROW_COUNTS:
        df = data[table_name]
        rows.append(
            {
                "tabela": table_name,
                "linhas": int(len(df)),
                "colunas": int(df.shape[1]),
                "duplicatas_exatas": int(df.duplicated().sum()),
                "ids_duplicados": int(df["id"].duplicated().sum()),
                "ids_nulos": int(df["id"].isna().sum()),
            }
        )
    return pd.DataFrame(rows)


def audit_relational_integrity(data: dict[str, pd.DataFrame]) -> dict[str, int]:
    """Audit referential (FK) and temporal integrity across all 6 transactional tables."""
    clientes = data["Clientes"]
    produtos = data["Produtos"]
    pedidos = data["Pedidos"]
    itens = data["Itens_Pedido"]
    tickets = data["Tickets_Suporte"]
    avaliacoes = data["Avaliacoes"]

    ped_cli = pedidos.merge(
        clientes[["id", "data_cadastro"]],
        left_on="cliente_id",
        right_on="id",
        how="left",
        suffixes=("", "_cli"),
    )

    return {
        "pedidos_sem_cliente_valido": int((~pedidos["cliente_id"].isin(clientes["id"])).sum()),
        "itens_sem_pedido_valido": int((~itens["pedido_id"].isin(pedidos["id"])).sum()),
        "itens_sem_produto_valido": int((~itens["produto_id"].isin(produtos["id"])).sum()),
        "pedidos_sem_nenhum_item": int((~pedidos["id"].isin(itens["pedido_id"])).sum()),
        "tickets_sem_pedido_valido": int((~tickets["pedido_id"].isin(pedidos["id"])).sum()),
        "avaliacoes_sem_pedido_valido": int((~avaliacoes["pedido_id"].isin(pedidos["id"])).sum()),
        "pedidos_antes_cadastro_cliente": int(
            (ped_cli["data_pedido"] < ped_cli["data_cadastro"]).sum()
        ),
        "tickets_resolucao_antes_abertura": int(
            (tickets["data_resolucao"] < tickets["data_abertura"]).sum()
        ),
        "tickets_resolvido_sem_data_resolucao": int(
            ((tickets["status"] == "resolvido") & (tickets["data_resolucao"].isna())).sum()
        ),
        "tickets_aberto_com_data_resolucao": int(
            ((tickets["status"] != "resolvido") & (tickets["data_resolucao"].notna())).sum()
        ),
    }
