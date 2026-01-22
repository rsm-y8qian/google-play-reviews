# src/fetch.py
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
from google_play_scraper import Sort, reviews

SORT_MAP = {
    "newest": Sort.NEWEST,
    "rating": Sort.RATING,
}

def fetch_reviews(
    app_id: str,
    out_csv: Path,
    lang: str = "en",
    country: str = "us",
    sort: str = "newest",
    batch_limit: int = 500,
    continuation_token: Optional[str] = None,
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Fetch up to batch_limit reviews and write to out_csv.
    Returns (df, next_token).
    """
    out_csv = Path(out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    all_rows = []
    token = continuation_token

    # google_play_scraper allows up to ~200 per request
    while len(all_rows) < batch_limit:
        count = min(200, batch_limit - len(all_rows))
        result, token = reviews(
            app_id,
            lang=lang,
            country=country,
            sort=SORT_MAP.get(sort, Sort.NEWEST),
            count=count,
            continuation_token=token,
        )

        if not result:
            break

        all_rows.extend(result)

        if token is None:
            break

    df = pd.DataFrame(all_rows)
    df.to_csv(out_csv, index=False)
    return df, token
