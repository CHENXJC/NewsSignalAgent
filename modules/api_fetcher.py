"""Conservative API adapter placeholder for explicitly configured public endpoints."""
from hashlib import sha256
from datetime import datetime, timezone
import os
import requests


def fetch_api_source(source_name: str, source_meta: dict, limit: int = 10) -> list[dict]:
    api_url = str(source_meta.get("api_url") or "").strip()
    if not api_url:
        return []
    key_env = str(source_meta.get("api_key_env") or "").strip()
    api_key = os.getenv(key_env, "") if key_env else ""
    if key_env and not api_key:
        return []
    headers = {"Accept": "application/json", "User-Agent": "NewsSignalAgent/NEWS-003"}
    if api_key:
        headers[str(source_meta.get("api_key_header") or "Authorization")] = f"Bearer {api_key}"
    try:
        response = requests.get(api_url, headers=headers, params={"limit": max(1, int(limit))}, timeout=15)
        response.raise_for_status()
        payload = response.json()
        items = payload if isinstance(payload, list) else next((payload.get(k, []) for k in ("articles", "items", "results") if isinstance(payload.get(k), list)), [])
        records = []
        for item in items[: max(0, int(limit))]:
            title = str(item.get("title", "")).strip()
            url = str(item.get("url", item.get("link", ""))).strip()
            digest = sha256(f"{source_name}|{title}|{url}".encode()).hexdigest()[:16]
            records.append({"id": f"api-{digest}", "title": title,
                "summary": str(item.get("summary", item.get("description", "")))[:1000],
                "source": source_name, "source_group": source_meta.get("source_group", "unknown"),
                "country_or_region": source_meta.get("country_or_region", "Unknown"),
                "published_at": item.get("published_at", item.get("published", "")),
                "topic": item.get("topic", "Unclassified"), "tags": "", "url": url,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "content_capture_policy": source_meta.get("content_capture_policy", "title_summary_link_only"),
                "source_verified_status": source_meta.get("verified_status", "needs_manual_check")})
        return records
    except (requests.RequestException, ValueError, TypeError):
        return []

# TODO NEWS-004: add provider-specific response mappers only for verified official APIs.
