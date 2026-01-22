from google_play_scraper import app as app_info
from src.utils import slugify

def resolve_slug_from_app_id(app_id: str) -> str:
    """
    Prefer human-readable title from Google Play. Fallback to last token of app_id.
    """
    try:
        info = app_info(app_id, lang="en", country="us")
        title = info.get("title")
        if title:
            return slugify(title)
    except Exception:
        pass

    # fallback: last token of package name
    return slugify(app_id.split(".")[-1])
