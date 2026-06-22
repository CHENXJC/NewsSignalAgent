"""Compliant RSS adapter: feed metadata only, never full article bodies."""
from hashlib import sha256
from html import unescape
import re
import feedparser
import requests
import truststore

truststore.inject_into_ssl()


def _plain_summary(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", str(value or ""))
    return re.sub(r"\s+", " ", unescape(text)).strip()[:1000]


def _topic(text: str) -> str:
    lowered = text.lower()
    rules = [("AI automation", (" ai ", "automation", "artificial intelligence")),
             ("Global trade", ("trade", "export", "supply chain")),
             ("Cost of living", ("inflation", "cost of living")),
             ("Energy transition", ("energy", "climate"))]
    padded = f" {lowered} "
    return next((topic for topic, terms in rules if any(term in padded for term in terms)), "Unclassified")


def fetch_rss_feed(source_name: str, source_meta: dict, limit: int = 10) -> list[dict]:
    feed_url = str(source_meta.get("feed_url") or "").strip()
    if not feed_url:
        return []
    try:
        response = requests.get(feed_url, timeout=15, headers={"User-Agent": "NewsSignalAgent/NEWS-004"}, stream=True)
        response.raise_for_status()
        content = bytearray()
        for chunk in response.iter_content(65536):
            content.extend(chunk)
            if len(content) >= 2_000_000:
                break
        parsed = feedparser.parse(bytes(content))
        if getattr(parsed, "bozo", False) and not getattr(parsed, "entries", []):
            return []
        articles = []
        for entry in list(getattr(parsed, "entries", []))[: max(0, int(limit))]:
            title = str(entry.get("title", "")).strip()
            url = str(entry.get("link", "")).strip()
            summary = _plain_summary(entry.get("summary", entry.get("description", "")))
            digest = sha256(f"{source_name}|{title}|{url}".encode("utf-8")).hexdigest()[:16]
            from datetime import datetime, timezone
            articles.append({"id": f"rss-{digest}", "title": title, "summary": summary,
                "source": source_name, "source_group": source_meta.get("source_group", "unknown"),
                "country_or_region": source_meta.get("country_or_region", "Unknown"),
                "published_at": entry.get("published", entry.get("updated", "")),
                "topic": _topic(f"{title} {summary}"), "tags": "", "url": url,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "content_capture_policy": source_meta.get("content_capture_policy", "title_summary_link_only"),
                "source_verified_status": source_meta.get("verified_status", "needs_manual_check")})
        return articles
    except Exception:
        return []
