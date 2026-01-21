import pandas as pd


def basic_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply basic data cleaning and transformation logic.

    This function is intended to contain all core transformation
    steps originally developed in exploratory notebooks, including:
    - Column renaming
    - Data type casting
    - Basic missing value handling
    - Creation of derived columns

    Parameters
    ----------
    df : pd.DataFrame
        Raw input DataFrame.

    Returns
    -------
    pd.DataFrame
        Cleaned and transformed DataFrame.
    """
    # Work on a copy to avoid mutating the input DataFrame
    df = df.copy()

    # Example: rename columns (replace with project-specific mappings)
    # df = df.rename(columns={"old_column_name": "new_column_name"})

    # Example: type casting
    # df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Drop rows that are completely empty
    df = df.dropna(how="all")

    # Example: create derived features
    # if "text" in df.columns:
    #     df["text_length"] = df["text"].astype(str).str.len()

    return df
