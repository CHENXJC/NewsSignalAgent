from modules.live_fetch_manager import fetch_enabled_sources


def test_disabled_and_no_url_sources_return_status_frames():
    config = {"source_groups": {"test_group": {"sources": {
        "disabled_one": {"country_or_region": "Global", "source_group": "test_group", "access_mode": "rss_future", "enabled": False},
        "missing_url": {"country_or_region": "Global", "source_group": "test_group", "access_mode": "rss_future", "enabled": True, "feed_url": ""},
    }}}}
    news, status = fetch_enabled_sources(config)
    assert news.empty
    assert list(status["status"]) == ["disabled", "no_url"]
    assert {"source", "items_fetched", "used_cache"}.issubset(status.columns)


def test_empty_config_returns_two_dataframes():
    news, status = fetch_enabled_sources({"source_groups": {}})
    assert hasattr(news, "columns") and hasattr(status, "columns")
