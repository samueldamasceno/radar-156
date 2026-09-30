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