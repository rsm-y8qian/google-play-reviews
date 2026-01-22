# src/transform.py
import pandas as pd
from typing import Tuple

def basic_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    """
    Minimal cleaning:
    - Drop fully empty rows
    - Ensure basic column types where obvious
    """
    df = df.copy()
    df = df.dropna(how="all")
    # example: ensure timestamp col parsed if exists
    if "timestamp" in df.columns:
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        except Exception:
            pass
    return df

def run_transforms(df: pd.DataFrame) -> pd.DataFrame:
    """
    Orchestrate transformations (extend this to add feature engineering)
    """
    df = basic_cleaning(df)
    # add any additional transformations here
    return df

