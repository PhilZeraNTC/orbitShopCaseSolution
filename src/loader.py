"""Data loading and schema typing for OrbitShop Due Diligence Series C."""

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

