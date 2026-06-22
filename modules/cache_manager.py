"""Per-source JSON cache with corruption-safe reads."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re


def _path(source_name: str, cache_dir: str) -> Path:
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", source_name).strip("._") or "unknown"
    return Path(cache_dir) / f"{safe_name}.json"


def save_fetch_cache(source_name: str, articles: list[dict], cache_dir: str = "cache/rss") -> str:
    path = _path(source_name, cache_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"source_name": source_name, "fetched_at": datetime.now(timezone.utc).isoformat(), "articles": articles}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return str(path)


def _payload(source_name: str, cache_dir: str) -> dict:
    try:
        data = json.loads(_path(source_name, cache_dir).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError, TypeError):
        return {}


def load_fetch_cache(source_name: str, cache_dir: str = "cache/rss") -> list[dict]:
    articles = _payload(source_name, cache_dir).get("articles", [])
    return articles if isinstance(articles, list) else []


def is_cache_fresh(source_name: str, max_age_minutes: int = 60, cache_dir: str = "cache/rss") -> bool:
    try:
        fetched = datetime.fromisoformat(str(_payload(source_name, cache_dir)["fetched_at"]).replace("Z", "+00:00"))
        if fetched.tzinfo is None:
            fetched = fetched.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - fetched).total_seconds() / 60
        return 0 <= age <= max(0, int(max_age_minutes))
    except (KeyError, TypeError, ValueError):
        return False
