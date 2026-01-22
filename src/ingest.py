# src/ingest.py
from pathlib import Path
import pandas as pd
from typing import Union

def ingest_from_csv(path: Union[str, Path]) -> pd.DataFrame:
    """
    Read raw CSV(s) from a file path or directory and return a single DataFrame.
    """
    p = Path(path)

    if not p.exists():
        raise FileNotFoundError(f"ingest path not found: {p}")

    if p.is_dir():
        files = sorted(p.glob("*.csv"))
        if not files:
            raise FileNotFoundError(f"No CSV files found under {p}")
        dfs = [pd.read_csv(f) for f in files]
        return pd.concat(dfs, ignore_index=True)

    # file
    if p.is_file():
        return pd.read_csv(p)

    raise FileNotFoundError(path)
