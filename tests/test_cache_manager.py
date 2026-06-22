from modules.cache_manager import is_cache_fresh, load_fetch_cache, save_fetch_cache


def test_save_load_and_freshness(tmp_path):
    cache_dir = str(tmp_path / "cache")
    articles = [{"id": "one", "title": "Example"}]
    save_fetch_cache("source/name", articles, cache_dir)
    assert load_fetch_cache("source/name", cache_dir) == articles
    assert is_cache_fresh("source/name", 60, cache_dir) is True


def test_missing_cache_is_safe(tmp_path):
    assert load_fetch_cache("missing", str(tmp_path)) == []
    assert isinstance(is_cache_fresh("missing", 60, str(tmp_path)), bool)
