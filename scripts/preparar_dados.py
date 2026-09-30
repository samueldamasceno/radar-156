from pathlib import Path

import numpy as np
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
    return (
        series
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
        .fillna("Não informado")
    )


def clean_district(series):
    series = (
        series
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

    numeric_mask = (
        series
        .str.fullmatch(
            r"\d+",
            na=False,
        )
    )

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
    print(f"Processando: {path.name}")
    print(f"Encoding: {encoding}")
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

        df = df[
            df["data_abertura"]
            .notna()
        ].copy()

        df["tema"] = clean_text(
            df["tema"]
        )

        df["servico"] = clean_text(
            df["servico"]
        )

        df["status"] = clean_text(
            df["status"]
        )

        df["distrito"] = clean_district(
            df["distrito"]
        )

        df["distrito_valido"] = (
            df["distrito"]
            .ne("Não informado")
        )

        status_upper = (
            df["status"]
            .str.upper()
            .str.strip()
        )

        df["pendente"] = (
            status_upper.isin(
                [
                    "ABERTO",
                    "EM ANDAMENTO",
                ]
            )
        ).astype("int8")

        df["finalizada"] = (
            status_upper
            .eq("FINALIZADA")
        ).astype("int8")

        df["cancelada"] = (
            status_upper
            .eq("CANCELADA")
        ).astype("int8")

        df["tempo_dias"] = (
            (
                df["data_finalizacao"]
                - df["data_abertura"]
            )
            .dt
            .total_seconds()
            / 86400
        )

        df.loc[
            status_upper.ne(
                "FINALIZADA"
            ),
            "tempo_dias",
        ] = np.nan

        df.loc[
            df["tempo_dias"] < 0,
            "tempo_dias",
        ] = np.nan

        df["semana"] = (
            df["data_abertura"]
            - pd.to_timedelta(
                df[
                    "data_abertura"
                ].dt.weekday,
                unit="D",
            )
        ).dt.normalize()

        df["linha"] = 1

        group_columns = [
            "semana",
            "tema",
            "servico",
            "distrito",
        ]

        grouped = (
            df.groupby(
                group_columns,
                dropna=False,
                observed=True,
            )
            .agg(
                solicitacoes=(
                    "linha",
                    "sum",
                ),
                pendentes=(
                    "pendente",
                    "sum",
                ),
                finalizadas=(
                    "finalizada",
                    "sum",
                ),
                canceladas=(
                    "cancelada",
                    "sum",
                ),
                tempo_total=(
                    "tempo_dias",
                    "sum",
                ),
                tempo_n=(
                    "tempo_dias",
                    "count",
                ),
            )
            .reset_index()
        )

        partial_results.append(
            grouped
        )

    return pd.concat(
        partial_results,
        ignore_index=True,
    )


# ============================================================
# LOCALIZA OS CSVs
# ============================================================

files = sorted(
    RAW_DIR.glob(
        "sp156_2026_q*.csv"
    )
)

if not files:
    raise FileNotFoundError(
        "Nenhum arquivo "
        "sp156_2026_q*.csv "
        "foi encontrado em "
        "data/raw/"
    )


# ============================================================
# PROCESSA TODOS OS ARQUIVOS
# ============================================================

results = []

for file in files:
    results.append(
        process_file(file)
    )


df = pd.concat(
    results,
    ignore_index=True,
)


# ============================================================
# CONSOLIDA OS CHUNKS
# ============================================================

GROUP_COLUMNS = [
    "semana",
    "tema",
    "servico",
    "distrito",
]


df = (
    df.groupby(
        GROUP_COLUMNS,
        observed=True,
        as_index=False,
    )
    .agg(
        solicitacoes=(
            "solicitacoes",
            "sum",
        ),
        pendentes=(
            "pendentes",
            "sum",
        ),
        finalizadas=(
            "finalizadas",
            "sum",
        ),
        canceladas=(
            "canceladas",
            "sum",
        ),
        tempo_total=(
            "tempo_total",
            "sum",
        ),
        tempo_n=(
            "tempo_n",
            "sum",
        ),
    )
)


# ============================================================
# MARCA DISTRITOS VÁLIDOS
# ============================================================

df["distrito_valido"] = (
    df["distrito"]
    .ne("Não informado")
)


# ============================================================
# INDICADORES OPERACIONAIS
# ============================================================

df["taxa_pendente"] = (
    df["pendentes"]
    / df[
        "solicitacoes"
    ].replace(
        0,
        np.nan,
    )
)


df["taxa_finalizacao"] = (
    df["finalizadas"]
    / df[
        "solicitacoes"
    ].replace(
        0,
        np.nan,
    )
)


df["taxa_cancelamento"] = (
    df["canceladas"]
    / df[
        "solicitacoes"
    ].replace(
        0,
        np.nan,
    )
)


df["tempo_medio_dias"] = (
    df["tempo_total"]
    / df[
        "tempo_n"
    ].replace(
        0,
        np.nan,
    )
)