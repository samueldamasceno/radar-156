from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")


arquivos = sorted(
    RAW_DIR.glob("sp156_2026_q*.csv")
)


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