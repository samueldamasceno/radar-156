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

    print(
        f"Total: {len(df):,}"
    )