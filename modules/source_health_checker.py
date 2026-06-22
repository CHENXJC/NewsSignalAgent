"""Small, bounded health checks for explicitly configured pilot RSS sources."""
from datetime import datetime, timezone
import feedparser
import pandas as pd
import requests
import truststore
from modules.source_manager import get_source_metadata

truststore.inject_into_ssl()

HEALTH_COLUMNS = ["source", "source_group", "country_or_region", "enabled", "access_mode", "feed_url",
                  "verified_status", "health_status", "http_status", "can_parse_feed", "entries_detected",
                  "message", "checked_at"]


def check_source_health(source_name: str, source_meta: dict, timeout_seconds: int = 10) -> dict:
    checked_at = datetime.now(timezone.utc).isoformat()
    enabled = bool(source_meta.get("enabled", False))
    feed_url = str(source_meta.get("feed_url") or "").strip()
    result = {"source": source_name, "source_group": source_meta.get("source_group", "unknown"),
              "country_or_region": source_meta.get("country_or_region", "Unknown"), "enabled": enabled,
              "access_mode": source_meta.get("access_mode", "demo_only"), "feed_url": feed_url,
              "verified_status": source_meta.get("verified_status", "needs_manual_check"), "http_status": None,
              "can_parse_feed": False, "entries_detected": 0, "checked_at": checked_at}
    if not enabled:
        return {**result, "health_status": "disabled", "message": "Source is disabled."}
    if not feed_url:
        return {**result, "health_status": "no_url", "message": "No feed URL configured."}
    try:
        response = requests.get(feed_url, timeout=max(1, int(timeout_seconds)),
                                headers={"User-Agent": "NewsSignalAgent/NEWS-004"}, stream=True)
        result["http_status"] = response.status_code
        response.raise_for_status()
        content = bytearray()
        for chunk in response.iter_content(65536):
            content.extend(chunk)
            if len(content) >= 2_000_000:
                break
        parsed = feedparser.parse(bytes(content))
        entries = len(getattr(parsed, "entries", []))
        parseable = entries > 0 and not (getattr(parsed, "bozo", False) and entries == 0)
        status = "healthy" if parseable else "warning"
        message = f"Feed parsed with {entries} entries." if parseable else "HTTP succeeded but no parseable entries were detected."
        return {**result, "health_status": status, "can_parse_feed": parseable,
                "entries_detected": entries, "message": message}
    except requests.RequestException as exc:
        return {**result, "health_status": "failed", "message": f"Request failed safely: {type(exc).__name__}."}
    except Exception as exc:
        return {**result, "health_status": "warning", "message": f"Feed check could not complete: {type(exc).__name__}."}


def check_pilot_sources(source_config: dict, pilot_config: dict) -> pd.DataFrame:
    records = []
    for source_name in pilot_config.get("sources", []):
        meta = get_source_metadata(source_name, source_config)
        if not meta:
            records.append({"source": source_name, "health_status": "skipped", "message": "Pilot source is missing from source configuration.",
                            "checked_at": datetime.now(timezone.utc).isoformat()})
        else:
            records.append(check_source_health(source_name, meta))
    return pd.DataFrame(records, columns=HEALTH_COLUMNS)
