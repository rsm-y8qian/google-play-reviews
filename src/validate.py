# src/validate.py
from typing import Dict, List
import pandas as pd

def validate_dataframe(df: pd.DataFrame, required_columns: List[str]=None) -> Dict:
    """
    Basic validation returning a serializable dict summarizing checks.
    """
    if required_columns is None:
        required_columns = []

    n = len(df)
    results = {}
    ok = True

    for col in required_columns:
        exists = col in df.columns
        missing_ratio = None
        col_ok = False
        if exists:
            missing_ratio = float(df[col].isna().mean())
            col_ok = missing_ratio == 0.0
        else:
            missing_ratio = None
            col_ok = False

        results[col] = {
            "exists": bool(exists),
            "missing_ratio": missing_ratio,
            "ok": bool(col_ok)
        }
        if not col_ok:
            ok = False

    return {
        "raw_count": n,
        "validations": results,
        "ok": bool(ok)
    }

