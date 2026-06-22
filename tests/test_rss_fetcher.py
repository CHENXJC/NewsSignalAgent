from types import SimpleNamespace
from modules import rss_fetcher


def test_missing_feed_url_returns_empty():
    assert rss_fetcher.fetch_rss_feed("example", {}) == []


def test_mocked_feed_is_normalized(monkeypatch):
    entry = {"title": "AI pilot expands", "summary": "<p>A short description.</p>", "link": "https://example.com/item", "published": "2026-01-01"}
    class Response:
        def raise_for_status(self): return None
        def iter_content(self, _): return [b"feed"]
    monkeypatch.setattr(rss_fetcher.requests, "get", lambda *args, **kwargs: Response())
    monkeypatch.setattr(rss_fetcher.feedparser, "parse", lambda _: SimpleNamespace(bozo=False, entries=[entry]))
    result = rss_fetcher.fetch_rss_feed("official_example", {"feed_url": "https://example.com/feed", "source_group": "us_wire", "country_or_region": "United States"})
    assert {"id", "title", "summary", "source", "source_group", "country_or_region", "published_at", "topic", "tags", "url", "fetched_at", "content_capture_policy", "source_verified_status"} == set(result[0])
    assert result[0]["summary"] == "A short description."
