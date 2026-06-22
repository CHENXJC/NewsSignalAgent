import requests
from modules import source_health_checker as checker


def test_disabled_source_returns_disabled():
    result = checker.check_source_health("off", {"enabled": False})
    assert result["health_status"] == "disabled"


def test_source_without_url_returns_no_url():
    result = checker.check_source_health("empty", {"enabled": True, "feed_url": ""})
    assert result["health_status"] == "no_url"


def test_invalid_url_does_not_crash(monkeypatch):
    def fail(*args, **kwargs):
        raise requests.ConnectionError("test failure")
    monkeypatch.setattr(checker.requests, "get", fail)
    result = checker.check_source_health("bad", {"enabled": True, "feed_url": "https://invalid.invalid/feed"})
    assert result["health_status"] == "failed"


def test_check_pilot_sources_returns_dataframe():
    config = {"source_groups": {"group": {"sources": {"off": {"enabled": False, "source_group": "group"}}}}}
    result = checker.check_pilot_sources(config, {"sources": ["off", "missing"]})
    assert list(result["health_status"]) == ["disabled", "skipped"]
