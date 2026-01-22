# src/transform.py
import pandas as pd

def run_transforms(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep this function as the single entrypoint for transformation logic.
    Extend here later (feature engineering, text cleaning, etc).
    """
    df = df.copy()

    # Drop fully empty rows
    df = df.dropna(how="all")

    # Example: standardize a common timestamp field if exists
    for col in ["at", "timestamp", "created_at", "date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            break

    return df

