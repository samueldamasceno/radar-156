from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURAÇÕES
# ============================================================

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

OUTPUT_FILE = (
    PROCESSED_DIR
    / "radar156.parquet"
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# COLUNAS UTILIZADAS
# ============================================================

COLUMN_MAP = {
    "Data de Abertura": "data_abertura",
    "Data de Finalização": "data_finalizacao",
    "Tema": "tema",
    "Serviço": "servico",
    "Status": "status",
    "Distrito": "distrito",
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def detect_format(path: Path):
    """
    Detecta encoding e separador do CSV.
    """

    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin1",
    ]

    separators = [
        ";",
        ",",
    ]

    for encoding in encodings:

        for separator in separators:

            try:

                sample = pd.read_csv(
                    path,
                    encoding=encoding,
                    sep=separator,
                    nrows=5,
                )

                if len(sample.columns) >= 15:

                    return (
                        encoding,
                        separator,
                    )

            except Exception:
                continue

    raise RuntimeError(
        f"Não foi possível identificar "
        f"o formato de {path}"
    )