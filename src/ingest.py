from pathlib import Path
import pandas as pd


def ingest_from_csv(path: str) -> pd.DataFrame:
    """
    Load raw CSV data from a file or a directory.

    If a directory is provided, all CSV files under the directory
    will be read and concatenated into a single DataFrame.

    Parameters
    ----------
    path : str
        Path to a CSV file or a directory containing CSV files.

    Returns
    -------
    pd.DataFrame
        Combined raw dataset.
    """
    p = Path(path)

    # If the path is a directory, read and concatenate all CSV files
    if p.is_dir():
        files = sorted(p.glob("*.csv"))
        if not files:
            raise FileNotFoundError(f"No CSV files found under {path}")

        dfs = [pd.read_csv(f) for f in files]
        df = pd.concat(dfs, ignore_index=True)

    # If the path is a single CSV file, read it directly
    elif p.is_file():
        df = pd.read_csv(p)

    # If the path does not exist, raise an explicit error
    else:
        raise FileNotFoundError(path)

    return df
