# src/utils.py
import re
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone

def app_id_from_play_url(url: str) -> str:
    qs = parse_qs(urlparse(url).query)
    app_id = qs.get("id", [None])[0]
    if not app_id:
        raise ValueError("Google Play URL missing '?id=<package_name>'")
    return app_id

def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "app"

def make_run_id_utc() -> str:
    # Windows-safe (no ":"), sortable, explicit UTC
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
