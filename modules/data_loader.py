"""Local demo-news loading and schema validation."""
from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = ["id", "title", "summary", "source", "source_group", "country_or_region", "published_at", "topic", "tags", "url"]


def validate_news_schema(df: pd.DataFrame) -> tuple[bool, list[str]]:
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    errors = [f"Missing required column: {column}" for column in missing]
    return not errors, errors


def load_demo_news(path: str) -> pd.DataFrame:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Demo news file not found: {file_path}")
    df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
    valid, errors = validate_news_schema(df)
    if not valid:
        raise ValueError("; ".join(errors))
    for column in df.select_dtypes(include="object"):
        df[column] = df[column].str.strip()
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")
    return df


def load_news_data(mode: str, demo_path: str, source_config_path: str | None = None,
                   limit_per_source: int = 10, use_cache: bool = True,
                   max_cache_age_minutes: int = 60, pilot_config: dict | None = None) -> tuple[pd.DataFrame, pd.DataFrame | None]:
    """Load demo, live, or hybrid data while preserving a stable schema."""
    normalized_mode = mode.strip().lower()
    if normalized_mode not in {"demo", "live", "hybrid"}:
        raise ValueError("mode must be 'demo', 'live', or 'hybrid'")
    demo_df = load_demo_news(demo_path) if normalized_mode in {"demo", "hybrid"} else pd.DataFrame(columns=REQUIRED_COLUMNS)
    if normalized_mode == "demo":
        return demo_df, None
    if not source_config_path:
        raise ValueError("source_config_path is required for live and hybrid modes")
    from modules.live_fetch_manager import fetch_enabled_sources
    from modules.source_manager import load_source_groups
    live_df, status_df = fetch_enabled_sources(load_source_groups(source_config_path), limit_per_source, use_cache,
                                               max_cache_age_minutes, pilot_config)
    if normalized_mode == "live":
        combined = live_df
    elif live_df.empty:
        combined = demo_df.copy()
    else:
        combined = pd.concat([demo_df, live_df], ignore_index=True)
    valid, errors = validate_news_schema(combined)
    if not valid:
        raise ValueError("; ".join(errors))
    combined["published_at"] = pd.to_datetime(combined["published_at"], errors="coerce", utc=True)
    return combined, status_df
