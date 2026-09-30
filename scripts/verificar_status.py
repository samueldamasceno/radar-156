import pandas as pd
from pathlib import Path


for file in sorted(
    Path("data/raw").glob("sp156_2026_q*.csv")
):
    print()
    print("=" * 80)
    print(file.name)

    df = pd.read_csv(
        file,
        sep=";",
        encoding="cp1252",
        usecols=[
            "Status",
            "Data de Finalização",
        ],
        dtype=str,
    )