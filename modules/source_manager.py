"""Source configuration helpers."""
from pathlib import Path
import pandas as pd
import yaml


def load_source_groups(config_path: str) -> dict:
    with Path(config_path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def get_source_metadata(source_name: str, source_config: dict) -> dict:
    groups = source_config.get("source_groups", source_config)
    for group_name, group_value in groups.items():
        sources = group_value.get("sources", group_value) if isinstance(group_value, dict) else {}
        if source_name in sources:
            metadata = dict(sources[source_name] or {})
            metadata.setdefault("source_group", group_name)
            return metadata
    return {}


def get_source_group_weight(source_group: str, scoring_config: dict) -> float:
    return float(scoring_config.get("source_group_weight_adjustments", {}).get(source_group, 1.0))


def list_available_sources(source_config: dict) -> pd.DataFrame:
    records = []
    groups = source_config.get("source_groups", source_config)
    for group_name, group_value in groups.items():
        sources = group_value.get("sources", group_value) if isinstance(group_value, dict) else {}
        for source_name, metadata in sources.items():
            record = {"source": source_name, **(metadata or {})}
            record.setdefault("source_group", group_name)
            records.append(record)
    return pd.DataFrame(records)
