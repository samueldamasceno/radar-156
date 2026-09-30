from pathlib import Path


RAW_DIR = Path("data/raw")


for file in sorted(RAW_DIR.glob("*.csv")):
    print("\n" + "=" * 80)
    print(f"ARQUIVO: {file}")