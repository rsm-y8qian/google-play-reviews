from typing import Dict
import pandas as pd


def validate_basic_counts(
    raw_df: pd.DataFrame,
    processed_df: pd.DataFrame
) -> Dict:
    """
    Validate basic row counts between raw and processed datasets.

    Parameters
    ----------
    raw_df : pd.DataFrame
        Raw input DataFrame.
    processed_df : pd.DataFrame
        Processed output DataFrame.

    Returns
    -------
    Dict
        Dictionary containing raw and processed row counts.
    """
    raw_count = len(raw_df)
    processed_count = len(processed_df)

    return {
        "raw_count": raw_count,
        "processed_count": processed_count,
    }


def validate_required_columns(
    df: pd.DataFrame,
    required: list,
    max_missing_ratio: float = 0.1
) -> Dict:
    """
    Check whether required columns exist and whether their missing
    ratios are within the acceptable threshold.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate.
    required : list
        List of required column names.
    max_missing_ratio : float, optional
        Maximum allowed missing ratio per column (default is 0.1).

    Returns
    -------
    Dict
        Summary dictionary describing existence, missing ratio,
        and validation status for each required column.
    """
    summary = {}

    for col in required:
        if col not in df.columns:
            summary[col] = {
                "exists": False,
                "missing_ratio": None,
                "ok": False,
            }
        else:
            missing_ratio = df[col].isna().mean()
            ok = missing_ratio <= max_missing_ratio

            summary[col] = {
                "exists": True,
                "missing_ratio": float(missing_ratio),
                "ok": ok,
            }

    return summary


def run_validations(raw_df, processed_df, required_cols=None) -> Dict:
    """
    Run all validation checks and aggregate results.

    Parameters
    ----------
    raw_df : pd.DataFrame
        Raw input DataFrame.
    processed_df : pd.DataFrame
        Processed output DataFrame.
    required_cols : list, optional
        List of required columns to validate.

    Returns
    -------
    Dict
        Aggregated validation results.
    """
    results = {}

    # Basic volume validation
    results.update(validate_basic_counts(raw_df, processed_df))

    # Required column validation
    if required_cols:
        results["required_columns"] = validate_required_columns(
            processed_df,
            required_cols
        )

    # Additional validations (e.g., value ranges, uniqueness)
    # can be added here as the pipeline evolves.

    return results
