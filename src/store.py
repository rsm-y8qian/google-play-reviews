# src/store.py
from pathlib import Path
import pandas as pd

def write_parquet_or_csv(df: pd.DataFrame, out_parquet: Path, prefer_parquet: bool = True) -> Path:
    out_parquet = Path(out_parquet)
    out_parquet.parent.mkdir(parents=True, exist_ok=True)

    if prefer_parquet:
        try:
            df.to_parquet(out_parquet, index=False)
            return out_parquet
        except Exception:
            # fallback to csv
            out_csv = out_parquet.with_suffix(".csv")
            df.to_csv(out_csv, index=False)
            return out_csv

    out_csv = out_parquet.with_suffix(".csv")
    df.to_csv(out_csv, index=False)
    return out_csv
