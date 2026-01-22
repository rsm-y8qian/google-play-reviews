# pipelines/run_pipeline.py
import argparse
import json
import traceback
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import yaml

from src.fetch import fetch_reviews
from src.transform import run_transforms
from src.validate import validate_dataframe
from src.store import write_parquet_or_csv
from src.utils import app_id_from_play_url, slugify

# Optional: try to resolve a human-friendly title from Google Play
try:
    from google_play_scraper import app as app_info
except Exception:
    app_info = None


def json_safe(obj):
    """Convert numpy/pandas types into JSON-safe python primitives."""
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_safe(v) for v in obj]
    return obj


def load_config(cfg_path: Path) -> dict:
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def make_run_id_utc() -> str:
    # Windows-safe, sortable, explicit UTC
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def resolve_app_slug(app_id: str, fallback: str | None = None, lang: str = "en", country: str = "us") -> str:
    """
    Create a friendly folder name for the app.
    Priority:
      1) Google Play title (if available) -> slugify(title)
      2) fallback string (e.g., user-provided) -> slugify(fallback)
      3) last token of app_id -> slugify(last token)
    """
    # 1) Try Google Play title
    if app_info is not None:
        try:
            info = app_info(app_id, lang=lang, country=country)
            title = info.get("title")
            if title:
                return slugify(title)
        except Exception:
            pass

    # 2) fallback
    if fallback:
        return slugify(fallback)

    # 3) last token
    return slugify(app_id.split(".")[-1])


def main(url: str, cfg_path: str = "config.yaml", batch_limit_override: int | None = None):
    base_dir = Path(__file__).resolve().parents[1]
    cfg = load_config(base_dir / cfg_path)

    # ---- resolve app_id from URL (most reliable) ----
    app_id = app_id_from_play_url(url)

    # ---- fetch defaults (also used for slug resolution) ----
    fetch_cfg = cfg.get("fetch", {})
    lang = fetch_cfg.get("lang", "en")
    country = fetch_cfg.get("country", "us")
    sort = fetch_cfg.get("sort", "newest")
    batch_limit = int(batch_limit_override or fetch_cfg.get("batch_limit", 500))

    # ---- build a friendly folder name (slug) ----
    # Use query-like fallback name from URL if you want; for now, no fallback needed
    app_slug = resolve_app_slug(app_id, fallback=None, lang=lang, country=country)

    # ---- roots from config ----
    raw_root = base_dir / cfg["paths"]["raw_root"]
    processed_root = base_dir / cfg["paths"]["processed_root"]
    runs_root = base_dir / cfg["paths"]["runs_root"]

    run_id = make_run_id_utc()
    run_dir = runs_root / app_slug / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # ---- app-specific paths (partitioned by run_id) ----
    raw_dir = raw_root / app_slug / run_id
    processed_file = processed_root / app_slug / run_id / "reviews.parquet"

    summary_path = run_dir / "run_summary.json"

    # ---- validation config ----
    required_columns = cfg.get("validation", {}).get("required_columns", [])

    # ---- store config ----
    prefer_parquet = bool(cfg.get("store", {}).get("prefer_parquet", True))

    # ---- summary skeleton ----
    start_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    summary = {
        "app": {
            "url": url,
            "id": app_id,
            "slug": app_slug,
        },
        "run_id": run_id,
        "start_time": start_time,
        "end_time": None,
        "status": "unknown",
        "errors": [],
        "counts": {"raw": None, "processed": None},
        "validation": None,
        "outputs": {
            "raw_dir": str(raw_dir),
            "processed_file": None,
            "run_dir": str(run_dir),
            "summary_path": str(summary_path),
            "raw_csv": None,
        },
        "fetch_params": {
            "lang": lang,
            "country": country,
            "sort": sort,
            "batch_limit": batch_limit,
        },
    }

    try:
        # ---- FETCH -> RAW ----
        raw_csv = raw_dir / "reviews_raw.csv"
        df_raw, _ = fetch_reviews(
            app_id=app_id,
            out_csv=raw_csv,
            lang=lang,
            country=country,
            sort=sort,
            batch_limit=batch_limit,
        )
        summary["counts"]["raw"] = int(len(df_raw))
        summary["outputs"]["raw_csv"] = str(raw_csv)

        print(f"[RESOLVE] app_id={app_id}  slug={app_slug}")
        print(f"[RAW] written to {raw_csv}")
        print(f"[INGEST] rows: {len(df_raw)}")

        # ---- TRANSFORM ----
        df_proc = run_transforms(df_raw)
        summary["counts"]["processed"] = int(len(df_proc))
        print(f"[TRANSFORM] rows: {len(df_proc)}")

        # ---- VALIDATE ----
        val = validate_dataframe(df_proc, required_columns=required_columns)
        summary["validation"] = val
        print("[VALIDATE] completed")

        # ---- STORE (latest snapshot in data/processed/<app_slug>/...) ----
        written = write_parquet_or_csv(df_proc, processed_file, prefer_parquet=prefer_parquet)
        summary["outputs"]["processed_file"] = str(written)
        print(f"[STORE] processed data written to {written}")

        summary["status"] = "success"

    except Exception as e:
        summary["status"] = "failed"
        summary["errors"].append(str(e))
        summary["errors"].append(traceback.format_exc())
        print("[ERROR] Pipeline failed:")
        print(traceback.format_exc())

    finally:
        summary["end_time"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(json_safe(summary), f, indent=2, ensure_ascii=False)

        print(f"[SUMMARY] written to {summary_path}")
        print(json.dumps(json_safe(summary), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Google Play reviews pipeline by pasting a Google Play URL"
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="Google Play URL containing ?id=<package_name>",
    )
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config yaml (repo-relative)")
    parser.add_argument("--batch_limit", type=int, default=None, help="Override batch_limit for this run")
    args = parser.parse_args()

    main(url=args.url, cfg_path=args.config, batch_limit_override=args.batch_limit)

