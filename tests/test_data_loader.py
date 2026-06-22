from pathlib import Path
from modules.data_loader import load_demo_news, validate_news_schema

ROOT = Path(__file__).parents[1]


def test_demo_csv_loads():
    df = load_demo_news(str(ROOT / "data" / "demo_news.csv"))
    assert len(df) >= 24


def test_schema_validation_passes():
    df = load_demo_news(str(ROOT / "data" / "demo_news.csv"))
    assert validate_news_schema(df) == (True, [])
