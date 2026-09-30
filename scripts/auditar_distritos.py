from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")


for arquivo in sorted(
    RAW_DIR.glob("sp156_2026_q*.csv")
):
    print()
    print("=" * 80)
    print(arquivo.name)

    df = pd.read_csv(
        arquivo,
        sep=";",
        encoding="cp1252",
        usecols=[
            "Distrito",
            "Latitude",
            "Longitude",
        ],
        dtype=str,
    )

    distrito = (
        df["Distrito"]
        .astype("string")
        .str.strip()
    )

    numerico = distrito.str.fullmatch(
        r"\d+",
        na=False,
    )

    nome = (
        distrito.notna()
        & ~numerico
    )

    ausente = distrito.isna()

    print(
        f"Total: {len(df):,}"
    )

    print(
        f"Com nome: {nome.sum():,} "
        f"({nome.mean() * 100:.2f}%)"
    )

    print(
        f"Com código numérico: {numerico.sum():,} "
        f"({numerico.mean() * 100:.2f}%)"
    )

    print(
        f"Sem distrito: {ausente.sum():,} "
        f"({ausente.mean() * 100:.2f}%)"
    )

    print()
    print("Top códigos numéricos:")

    print(
        distrito[numerico]
        .value_counts()
        .head(20)
        .to_string()
    )