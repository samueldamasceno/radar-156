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


def clean_text(series):
    """
    Padroniza campos de texto.
    """

    return (
        series
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
        .fillna("Não informado")
    )


def clean_district(series):
    """
    Trata o campo Distrito.

    A base possui:
    - nomes de distritos;
    - códigos numéricos;
    - valores ausentes.

    Para o MVP, somente nomes de distritos
    são considerados territorialmente válidos.
    """

    series = (
        series
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

    # Identifica valores compostos
    # somente por números.
    numeric_mask = (
        series
        .str.fullmatch(
            r"\d+",
            na=False,
        )
    )

    # Códigos numéricos são transformados
    # em valores não identificados.
    series = series.mask(
        numeric_mask,
        pd.NA,
    )

    return series.fillna(
        "Não informado"
    )


# ============================================================
# PROCESSAMENTO DE CADA CSV
# ============================================================

def process_file(path: Path):

    encoding, separator = (
        detect_format(path)
    )

    print()
    print("=" * 80)

    print(
        f"Processando: {path.name}"
    )

    print(
        f"Encoding: {encoding}"
    )

    print(
        f"Separador: "
        f"{repr(separator)}"
    )

    partial_results = []

    reader = pd.read_csv(
        path,
        encoding=encoding,
        sep=separator,
        dtype=str,
        chunksize=150_000,
        low_memory=False,
    )

    for chunk_number, chunk in enumerate(
        reader,
        start=1,
    ):

        print(
            f"  Processando chunk "
            f"{chunk_number}"
        )

        # ---------------------------------
        # CONFERE COLUNAS
        # ---------------------------------

        missing_columns = [
            column
            for column
            in COLUMN_MAP.keys()
            if column not in chunk.columns
        ]

        if missing_columns:

            raise ValueError(
                "Colunas ausentes: "
                + ", ".join(
                    missing_columns
                )
            )

        # ---------------------------------
        # SELEÇÃO E RENOMEAÇÃO
        # ---------------------------------

        df = (
            chunk[
                list(
                    COLUMN_MAP.keys()
                )
            ]
            .copy()
            .rename(
                columns=COLUMN_MAP
            )
        )

        # ---------------------------------
        # DATAS
        # ---------------------------------

        df["data_abertura"] = (
            pd.to_datetime(
                df["data_abertura"],
                errors="coerce",
                dayfirst=True,
            )
        )

        df["data_finalizacao"] = (
            pd.to_datetime(
                df["data_finalizacao"],
                errors="coerce",
                dayfirst=True,
            )
        )

        # Remove registros sem
        # data de abertura válida.
        df = df[
            df["data_abertura"]
            .notna()
        ].copy()

        # ---------------------------------
        # CAMPOS DE TEXTO
        # ---------------------------------

        df["tema"] = clean_text(
            df["tema"]
        )

        df["servico"] = clean_text(
            df["servico"]
        )

        df["status"] = clean_text(
            df["status"]
        )

        df["distrito"] = (
            clean_district(
                df["distrito"]
            )
        )

        # ---------------------------------
        # DISTRITO VÁLIDO
        # ---------------------------------

        df["distrito_valido"] = (
            df["distrito"]
            .ne("Não informado")
        )

        partial_results.append(
            df
        )

    return pd.concat(
        partial_results,
        ignore_index=True,
    )