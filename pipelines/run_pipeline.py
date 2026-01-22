# pipelines/run_pipeline.py
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import yaml
import traceback

import pandas as pd
import numpy as np

# local modules
from src.ingest import ingest_from_csv
from src.transform import run_transforms
from src.validate import validate_dataframe
from src.store import write_parquet, write_csv

# ---------------- helpers ----------------
def json_safe(obj):
    """Convert common non-JSON-serializable objects (numpy, pandas types) to plain python types."""
    if isinstance(obj, (np.bool_, )):
        return bool(obj)
    if isinstance(obj, (np.integer, )):
        return int(obj)
    if isinstance(obj, (np.floating, )):
        return float(obj)
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_safe(v) for v in obj]
    return obj

def load_config(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# ---------------- main ----------------
def main(cfg_path: str = "config.yaml"):
    base = Path(__file__).resolve().parents[1]
    cfg = load_config(base / cfg_path)

    # data layer paths
    raw_dir = base / Path(cfg["data"]["raw_dir"])
    processed_file = base / Path(cfg["data"]["processed_file"])

    # run outputs
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    runs_dir = base / Path(cfg["outputs"]["runs_dir"])
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    summary_path = run_dir / "run_summary.json"
    processed_written_path = None

    # summary skeleton
    summary = {
        "run_id": run_id,
        "start_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "errors": [],
        "raw_count": None,
        "processed_count": None,
        "validations": {},
        "outputs": {}
    }

    try:
        # INGEST
        df_raw = ingest_from_csv(raw_dir)
        summary["raw_count"] = int(len(df_raw))
        print(f"[INGEST] rows: {len(df_raw)}")

        # TRANSFORM
        df_proc = run_transforms(df_raw)
        summary["processed_count"] = int(len(df_proc))
        print(f"[TRANSFORM] rows: {len(df_proc)}")

        # VALIDATE
        required_cols = cfg.get("validation", {}).get("required_columns", [])
        val = validate_dataframe(df_proc, required_columns=required_cols)
        summary["validations"] = val
        print("[VALIDATE] completed")

        # STORE: first, try to write the canonical snapshot to data/processed
        # Prefer parquet when configured and engine available
        prefer_parquet = cfg.get("store", {}).get("parquet_prefer", True)
        try:
            if prefer_parquet:
                write_parquet(df_proc, processed_file)
                processed_written_path = processed_file
            else:
                # fallback to csv with .csv extension
                csv_path = processed_file.with_suffix(".csv")
                write_csv(df_proc, csv_path)
                processed_written_path = csv_path
            print(f"[STORE] processed data written to {processed_written_path}")
        except Exception as e:
            # attempt fallback to csv in outputs run dir
            fallback = run_dir / "processed.csv"
            try:
                write_csv(df_proc, fallback)
                processed_written_path = fallback
                print(f"[STORE] parquet write failed, fallback CSV written to {fallback}")
            except Exception as ee:
                raise RuntimeError(f"Write failed both parquet and csv: {e}; {ee}")

        # record outputs in summary
        summary["outputs"]["processed_data"] = str(processed_written_path)
        summary["outputs"]["run_summary"] = str(summary_path)

    except Exception as e:
        tb = traceback.format_exc()
        summary["errors"].append(str(e))
        summary["errors"].append(tb)
        print("[ERROR] Pipeline failed:")
        print(tb)

    finally:
        # always set end_time and write summary (observability)
        summary["end_time"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(json_safe(summary), f, indent=2, ensure_ascii=False)
        print(f"[SUMMARY] written to {summary_path}")
        # also print summary safely
        print(json.dumps(json_safe(summary), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # allow override of config file path via CLI
    cfg_arg = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    main(cfg_arg)
