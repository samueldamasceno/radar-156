from pathlib import Path


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