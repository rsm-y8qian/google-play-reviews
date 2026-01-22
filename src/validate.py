# src/validate.py
from typing import Dict, List
import pandas as pd

def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> Dict:
    """
    Returns a JSON-serializable validation report.
    """
    report = {
        "row_count": int(len(df)),
        "required_columns": {},
        "ok": True,
    }

    for col in required_columns:
        exists = col in df.columns
        missing_ratio = None
        col_ok = False

        if exists:
            missing_ratio = float(df[col].isna().mean())
            # you can relax this rule later; for now strict is fine
            col_ok = missing_ratio == 0.0

        report["required_columns"][col] = {
            "exists": bool(exists),
            "missing_ratio": missing_ratio,
            "ok": bool(col_ok),
        }

        if not col_ok:
            report["ok"] = False

    return report


