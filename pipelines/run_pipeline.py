import sys
from pathlib import Path
import json
from datetime import datetime
import argparse

import pandas as pd
import yaml

from src.ingest import ingest_from_csv
from src.transform import run_transforms
from src.validate import run_validations
from src.store import store_parquet


def load_config(path: str = "config.yaml"):
    """
    Load pipeline configuration from a YAML file.

    If the file does not exist, a default configuration
    will be returned.

    Parameters
    ----------
    path : str
        Path to the configuration file.

    Returns
    -------
    dict
        Configuration dictionary.
    """
    p = Path(path)

    if p.exists():
        return yaml.safe_load(p.read_text())
    else:
        # Default configuration (can be customized)
        return {
            "raw_path": "data/raw",
            "output_path": "outputs/processed.parquet",
            "summary_path": "outputs/run_summary.json",
            "required_columns": [],
            "output_format": "parquet",
        }


def main(cfg: dict):
    """
    Run the end-to-end data pipeline:
    ingest -> transform -> validate -> store.
    """
    start_time = datetime.utcnow().isoformat() + "Z"
    summary = {
        "start_time": start_time,
        "errors": [],
    }

    try:
        # 1) Ingest raw data
        raw_df = ingest_from_csv(cfg["raw_path"])
        summary["raw_count"] = len(raw_df)
        print(f"[INGEST] rows: {len(raw_df)}")

        # 2) Apply transformations
        processed_df = run_transforms(raw_df)
        summary["processed_count"] = len(processed_df)
        print(f"[TRANSFORM] rows: {len(processed_df)}")

        # 3) Run validation checks
        validation_results = run_validations(
            raw_df,
            processed_df,
            cfg.get("required_columns")
        )
        summary["validations"] = validation_results
        print("[VALIDATE] completed")

        # 4) Store processed output
        store_parquet(processed_df, cfg["output_path"])
        print(f"[STORE] output written to {cfg['output_path']}")

    except Exception as e:
        import traceback
        summary["errors"].append(str(e))
        summary["traceback"] = traceback.format_exc()
        print("[ERROR]", e, file=sys.stderr)

    finally:
        # Always write run summary for observability
        end_time = datetime.utcnow().isoformat() + "Z"
        summary["end_time"] = end_time

        summary_path = Path(cfg["summary_path"])
        summary_path.parent.mkdir(parents=True, exist_ok=True)

        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"[SUMMARY] written to {cfg['summary_path']}")
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the end-to-end data pipeline"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to pipeline configuration file",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)
    main(cfg)
