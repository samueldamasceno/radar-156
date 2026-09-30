from pathlib import Path
import re
import unicodedata

import pandas as pd


RAW_DIR = Path("data/raw")


def normalizar_texto(valor):
    if pd.isna(valor):
        return "NAO INFORMADO"

    valor = str(valor).strip().upper()

    # Remove acentos
    valor = unicodedata.normalize("NFKD", valor)
    valor = "".join(
        char
        for char in valor
        if not unicodedata.combining(char)
    )

    # Padroniza diferentes tipos de apóstrofo
    valor = valor.replace("’", "'")
    valor = valor.replace("`", "'")

    # Remove espaços duplicados
    valor = re.sub(r"\s+", " ", valor)

    return valor


arquivos = sorted(
    RAW_DIR.glob("sp156_2026_q*.csv")
)

frames = []


for arquivo in arquivos:

    print()
    print("=" * 80)
    print(f"ARQUIVO: {arquivo.name}")

    df = pd.read_csv(
        arquivo,
        sep=";",
        encoding="cp1252",
        usecols=[
            "Distrito",
            "Prefeitura Operacional",
        ],
        dtype=str,
    )

    print()

    print(
        "Distritos únicos originais:",
        df["Distrito"].nunique(dropna=True),
    )

    print(
        "Prefeituras operacionais únicas:",
        df["Prefeitura Operacional"].nunique(
            dropna=True
        ),
    )

    df["distrito_normalizado"] = (
        df["Distrito"]
        .apply(normalizar_texto)
    )

    df["prefeitura_normalizada"] = (
        df["Prefeitura Operacional"]
        .apply(normalizar_texto)
    )

    print(
        "Distritos após normalização:",
        df["distrito_normalizado"].nunique(),
    )

    print(
        "Prefeituras após normalização:",
        df["prefeitura_normalizada"].nunique(),
    )

    df["arquivo"] = arquivo.name

    frames.append(df)


todos = pd.concat(
    frames,
    ignore_index=True,
)


print()
print("=" * 80)
print("BASE COMPLETA")
print("=" * 80)

print()
print(
    "Distritos originais:",
    todos["Distrito"].nunique(dropna=True),
)

print(
    "Distritos normalizados:",
    todos["distrito_normalizado"].nunique(),
)

print()
print(
    "Prefeituras originais:",
    todos["Prefeitura Operacional"].nunique(
        dropna=True
    ),
)

print(
    "Prefeituras normalizadas:",
    todos["prefeitura_normalizada"].nunique(),
)


# ============================================================
# PROCURA NOMES DIFERENTES QUE VIRAM O MESMO NOME NORMALIZADO
# ============================================================

print()
print("=" * 80)
print("POSSÍVEIS DUPLICIDADES DE DISTRITO")
print("=" * 80)


distritos = (
    todos[
        [
            "Distrito",
            "distrito_normalizado",
        ]
    ]
    .drop_duplicates()
    .dropna(subset=["Distrito"])
)


duplicados_distrito = (
    distritos.groupby(
        "distrito_normalizado"
    )["Distrito"]
    .agg(list)
)


duplicados_distrito = (
    duplicados_distrito[
        duplicados_distrito.apply(len) > 1
    ]
)


if duplicados_distrito.empty:
    print(
        "Nenhuma duplicidade simples "
        "encontrada."
    )
else:
    for nome, variantes in (
        duplicados_distrito.items()
    ):
        print()
        print(nome)
        print("  ", variantes)


print()
print("=" * 80)
print("POSSÍVEIS DUPLICIDADES DE PREFEITURA")
print("=" * 80)


prefeituras = (
    todos[
        [
            "Prefeitura Operacional",
            "prefeitura_normalizada",
        ]
    ]
    .drop_duplicates()
    .dropna(
        subset=[
            "Prefeitura Operacional"
        ]
    )
)


duplicados_prefeitura = (
    prefeituras.groupby(
        "prefeitura_normalizada"
    )["Prefeitura Operacional"]
    .agg(list)
)


duplicados_prefeitura = (
    duplicados_prefeitura[
        duplicados_prefeitura.apply(len) > 1
    ]
)


if duplicados_prefeitura.empty:
    print(
        "Nenhuma duplicidade simples "
        "encontrada."
    )
else:
    for nome, variantes in (
        duplicados_prefeitura.items()
    ):
        print()
        print(nome)
        print("  ", variantes)


# ============================================================
# LISTA COMPLETA
# ============================================================

print()
print("=" * 80)
print("LISTA DOS DISTRITOS NORMALIZADOS")
print("=" * 80)

for nome in sorted(
    todos[
        "distrito_normalizado"
    ].unique()
):
    print(nome)


print()
print("=" * 80)
print("LISTA DAS PREFEITURAS NORMALIZADAS")
print("=" * 80)

for nome in sorted(
    todos[
        "prefeitura_normalizada"
    ].unique()
):
    print(nome)