from pathlib import Path
import pandas as pd


def store_parquet(
    df: pd.DataFrame,
    path: str,
    overwrite: bool = True
):
    """
    Store a DataFrame as a Parquet file.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to store.
    path : str
        Output file path.
    overwrite : bool, optional
        Whether to overwrite the file if it already exists.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    if p.exists() and not overwrite:
        raise FileExistsError(path)

    df.to_parquet(p, index=False)


def store_csv(
    df: pd.DataFrame,
    path: str,
    overwrite: bool = True
):
    """
    Store a DataFrame as a CSV file.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to store.
    path : str
        Output file path.
    overwrite : bool, optional
        Whether to overwrite the file if it already exists.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(p, index=False)
