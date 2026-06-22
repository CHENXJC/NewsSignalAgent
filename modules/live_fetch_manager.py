"""Orchestrate optional live adapters without allowing one source to break a run."""
import pandas as pd
from modules.api_fetcher import fetch_api_source
from modules.cache_manager import is_cache_fresh, load_fetch_cache, save_fetch_cache
from modules.data_loader import REQUIRED_COLUMNS
from modules.rss_fetcher import fetch_rss_feed

STATUS_COLUMNS = ["source", "source_group", "country_or_region", "access_mode", "enabled", "status", "items_fetched", "used_cache", "message"]
LIVE_COLUMNS = REQUIRED_COLUMNS + ["fetched_at", "content_capture_policy", "source_verified_status"]


def _sources(source_config: dict):
    for group_name, group in source_config.get("source_groups", source_config).items():
        entries = group.get("sources", {}) if isinstance(group, dict) else {}
        for name, raw_meta in entries.items():
            meta = dict(raw_meta or {})
            meta.setdefault("source_group", group_name)
            yield name, meta


def fetch_enabled_sources(source_config: dict, limit_per_source: int = 10, use_cache: bool = True,
                          max_cache_age_minutes: int = 60, pilot_config: dict | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_articles, statuses = [], []
    configured_sources = list(_sources(source_config))
    if pilot_config is not None:
        pilot_names = set(pilot_config.get("sources", []))
        configured_sources = [(name, meta) for name, meta in configured_sources if name in pilot_names]
    configured_sources.sort(key=lambda item: int(item[1].get("fetch_priority", 999)))
    max_total = int(pilot_config.get("max_total_items", 0)) if pilot_config else 0
    for source_name, meta in configured_sources:
        mode = str(meta.get("access_mode", "demo_only")).lower()
        enabled = bool(meta.get("enabled", False))
        base = {"source": source_name, "source_group": meta.get("source_group", "unknown"),
                "country_or_region": meta.get("country_or_region", "Unknown"), "access_mode": mode,
                "enabled": enabled, "items_fetched": 0, "used_cache": False}
        if not enabled:
            statuses.append({**base, "status": "disabled", "message": "Live fetching is disabled."})
            continue
        if mode == "demo_only":
            statuses.append({**base, "status": "skipped", "message": "Demo-only source."})
            continue
        is_rss, is_api = "rss" in mode, "api" in mode
        url = str(meta.get("feed_url" if is_rss else "api_url" if is_api else "feed_url", "") or "").strip()
        if not url:
            statuses.append({**base, "status": "no_url", "message": "No live URL configured."})
            continue
        remaining = max_total - len(all_articles) if max_total else int(limit_per_source)
        if max_total and remaining <= 0:
            statuses.append({**base, "status": "skipped", "message": "Pilot maximum total items reached."})
            continue
        source_limit = min(max(1, int(limit_per_source)), max(1, int(meta.get("fetch_limit", limit_per_source))), remaining)
        cached = load_fetch_cache(source_name)
        if use_cache and is_cache_fresh(source_name, max_cache_age_minutes) and cached:
            all_articles.extend(cached[:source_limit])
            statuses.append({**base, "status": "cache_used", "items_fetched": len(cached[:source_limit]),
                             "used_cache": True, "message": "Fresh local cache used."})
            continue
        try:
            articles = fetch_rss_feed(source_name, meta, source_limit) if is_rss else fetch_api_source(source_name, meta, source_limit) if is_api else []
            if articles:
                save_fetch_cache(source_name, articles)
                all_articles.extend(articles)
                statuses.append({**base, "status": "success", "items_fetched": len(articles), "message": "Live metadata fetched."})
            elif use_cache and cached:
                all_articles.extend(cached[:source_limit])
                statuses.append({**base, "status": "cache_used", "items_fetched": len(cached[:source_limit]),
                                 "used_cache": True, "message": "Live fetch returned no items; stale cache used."})
            else:
                statuses.append({**base, "status": "failed", "message": "Live fetch returned no usable items."})
        except Exception as exc:
            if use_cache and cached:
                all_articles.extend(cached[:source_limit])
                statuses.append({**base, "status": "cache_used", "items_fetched": len(cached[:source_limit]),
                                 "used_cache": True, "message": "Fetch failed; available cache used."})
            else:
                statuses.append({**base, "status": "failed", "message": f"Fetch failed safely: {type(exc).__name__}"})
    news_df = pd.DataFrame(all_articles, columns=LIVE_COLUMNS)
    status_df = pd.DataFrame(statuses, columns=STATUS_COLUMNS)
    return news_df, status_df
