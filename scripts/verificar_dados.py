from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")


def detect_format(path: Path):
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
    separators = [";", ","]

    for encoding in encodings:
        for separator in separators:
            try:
                df = pd.read_csv(
                    path,
                    encoding=encoding,
                    sep=separator,
                    nrows=5,
                )

                if len(df.columns) >= 10:
                    return encoding, separator

            except Exception:
                continue

    raise RuntimeError(f"Não consegui identificar o formato de {path}")


for file in sorted(RAW_DIR.glob("*.csv")):
    print("\n" + "=" * 80)
    print(f"ARQUIVO: {file}")

    encoding, separator = detect_format(file)

    print(f"Encoding: {encoding}")
    print(f"Separador: {repr(separator)}")