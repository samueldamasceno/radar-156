from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


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

        # ---------------------------------
        # STATUS
        # ---------------------------------

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

        # ---------------------------------
        # TEMPO DE ATENDIMENTO
        # ---------------------------------

        df["tempo_dias"] = (
            (
                df["data_finalizacao"]
                - df["data_abertura"]
            )
            .dt
            .total_seconds()
            / 86400
        )

        # Só consideramos tempo
        # de atendimento de solicitações
        # efetivamente finalizadas.
        df.loc[
            status_upper.ne(
                "FINALIZADA"
            ),
            "tempo_dias",
        ] = np.nan

        # Remove tempos impossíveis.
        df.loc[
            df["tempo_dias"] < 0,
            "tempo_dias",
        ] = np.nan

        # ---------------------------------
        # SEMANA
        # ---------------------------------

        # A semana passa a ser identificada
        # pela segunda-feira correspondente.

        df["semana"] = (
            df["data_abertura"]
            - pd.to_timedelta(
                df[
                    "data_abertura"
                ].dt.weekday,
                unit="D",
            )
        ).dt.normalize()

        # ---------------------------------
        # AGREGAÇÃO
        # ---------------------------------

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


# ============================================================
# ORDENAÇÃO TEMPORAL
# ============================================================

df = df.sort_values(
    [
        "tema",
        "distrito",
        "servico",
        "semana",
    ]
).reset_index(
    drop=True
)


# ============================================================
# BASELINE HISTÓRICA
# ============================================================

group_keys = [
    "tema",
    "distrito",
    "servico",
]


# Média das quatro observações
# anteriores disponíveis para
# a mesma combinação.
df["volume_baseline"] = (
    df.groupby(
        group_keys
    )["solicitacoes"]
    .transform(
        lambda series:
        series
        .shift(1)
        .rolling(
            window=4,
            min_periods=2,
        )
        .mean()
    )
)


# ============================================================
# VARIAÇÃO DA DEMANDA
# ============================================================

df["variacao"] = (
    df["solicitacoes"]
    / df[
        "volume_baseline"
    ].replace(
        0,
        np.nan,
    )
    - 1
)


df["variacao"] = (
    df["variacao"]
    .replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )
)


df["variacao_percentual"] = (
    df["variacao"]
    * 100
).round(1)


df["crescimento_positivo"] = (
    df["variacao"]
    .fillna(0)
    .clip(
        lower=0
    )
)


# ============================================================
# NORMALIZAÇÃO
# ============================================================

valid_mask = (
    df["distrito_valido"]
)


def percentile_score(series):
    """
    Calcula percentil somente
    para registros com distrito
    territorialmente válido.
    """

    result = pd.Series(
        np.nan,
        index=series.index,
        dtype=float,
    )

    values = (
        series.loc[
            valid_mask
        ]
        .fillna(0)
    )

    result.loc[
        valid_mask
    ] = (
        values
        .rank(
            pct=True
        )
        .mul(100)
    )

    return result


df["score_crescimento"] = (
    percentile_score(
        df[
            "crescimento_positivo"
        ]
    )
)


df["score_pendencia"] = (
    percentile_score(
        df[
            "taxa_pendente"
        ]
    )
)


df["score_tempo"] = (
    percentile_score(
        df[
            "tempo_medio_dias"
        ]
    )
)


# ============================================================
# ÍNDICE DE ATENÇÃO
# ============================================================

df["indice_atencao"] = (
    0.40
    * df["score_crescimento"]

    + 0.35
    * df["score_pendencia"]

    + 0.25
    * df["score_tempo"]
).round(1)


# Registros sem distrito válido
# não recebem índice territorial.
df.loc[
    ~valid_mask,
    "indice_atencao",
] = np.nan


# ============================================================
# DETECÇÃO DE ANOMALIAS
# ============================================================

# O modelo também é treinado somente
# com observações territorialmente
# identificáveis.

model_data = pd.DataFrame(
    {
        "volume":
        np.log1p(
            df.loc[
                valid_mask,
                "solicitacoes",
            ]
        ),

        "crescimento":
        df.loc[
            valid_mask,
            "crescimento_positivo",
        ].clip(
            upper=5
        ),

        "pendencia":
        df.loc[
            valid_mask,
            "taxa_pendente",
        ].fillna(0),

        "tempo":
        np.log1p(
            df.loc[
                valid_mask,
                "tempo_medio_dias",
            ].fillna(0)
        ),
    }
)


scaler = StandardScaler()

X = scaler.fit_transform(
    model_data
)


model = IsolationForest(
    n_estimators=200,

    # O MVP define 3% das observações
    # como o conjunto de maior atipicidade.
    contamination=0.03,

    random_state=42,
)


predictions = (
    model.fit_predict(X)
)


# Inicializa como falso para
# todo o dataset.
df["anomalia"] = False


df.loc[
    valid_mask,
    "anomalia",
] = (
    predictions == -1
)


# ============================================================
# SCORE DE ANOMALIA
# ============================================================

raw_anomaly_score = (
    -model.decision_function(
        X
    )
)


ranked_anomaly_score = (
    pd.Series(
        raw_anomaly_score,
        index=df.index[
            valid_mask
        ],
    )
    .rank(
        pct=True
    )
    .mul(100)
    .round(1)
)


df["score_anomalia"] = (
    np.nan
)


df.loc[
    valid_mask,
    "score_anomalia",
] = (
    ranked_anomaly_score
)


# ============================================================
# FAIXA DE ATENÇÃO
# ============================================================

def faixa_atencao(score):

    if pd.isna(score):
        return "Não aplicável"

    if score >= 75:
        return "Elevada"

    if score >= 50:
        return "Moderada"

    return "Regular"


df["faixa_atencao"] = (
    df[
        "indice_atencao"
    ]
    .apply(
        faixa_atencao
    )
)


# ============================================================
# DATASET FINAL
# ============================================================

columns_to_save = [
    "semana",
    "tema",
    "servico",
    "distrito",
    "distrito_valido",
    "solicitacoes",
    "pendentes",
    "finalizadas",
    "canceladas",
    "taxa_pendente",
    "taxa_finalizacao",
    "taxa_cancelamento",
    "tempo_medio_dias",
    "volume_baseline",
    "variacao_percentual",
    "score_crescimento",
    "score_pendencia",
    "score_tempo",
    "indice_atencao",
    "faixa_atencao",
    "anomalia",
    "score_anomalia",
]


final_df = (
    df[
        columns_to_save
    ]
    .copy()
)


# ============================================================
# SALVA PARQUET
# ============================================================

final_df.to_parquet(
    OUTPUT_FILE,
    index=False,
)


# ============================================================
# RESUMO DA EXECUÇÃO
# ============================================================

total_solicitacoes = int(
    final_df[
        "solicitacoes"
    ].sum()
)


solicitacoes_territoriais = int(
    final_df.loc[
        final_df[
            "distrito_valido"
        ],
        "solicitacoes",
    ].sum()
)


cobertura_territorial = (
    solicitacoes_territoriais
    / total_solicitacoes
    * 100
)


distritos_validos = (
    final_df.loc[
        final_df[
            "distrito_valido"
        ],
        "distrito",
    ]
    .nunique()
)


anomalias = int(
    final_df[
        "anomalia"
    ].sum()
)


print()
print("=" * 80)

print(
    "PROCESSAMENTO CONCLUÍDO"
)

print("=" * 80)

print(
    f"Solicitações processadas: "
    f"{total_solicitacoes:,}"
)

print(
    f"Solicitações com distrito válido: "
    f"{solicitacoes_territoriais:,}"
)

print(
    f"Cobertura territorial: "
    f"{cobertura_territorial:.1f}%"
)

print(
    f"Linhas analíticas: "
    f"{len(final_df):,}"
)

print(
    f"Distritos válidos: "
    f"{distritos_validos:,}"
)

print(
    f"Temas: "
    f"{final_df['tema'].nunique():,}"
)

print(
    f"Serviços: "
    f"{final_df['servico'].nunique():,}"
)

print(
    f"Semanas: "
    f"{final_df['semana'].nunique():,}"
)

print(
    f"Anomalias territoriais: "
    f"{anomalias:,}"
)

print()

print(
    f"Arquivo salvo em: "
    f"{OUTPUT_FILE}"
)

print()

print(
    "Primeiras linhas:"
)

print(
    final_df.head()
)