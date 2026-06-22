from pathlib import Path
import yaml
from modules.source_manager import get_source_metadata, load_source_groups

ROOT = Path(__file__).parents[1]


def test_pilot_config_is_non_empty_and_sources_exist():
    with (ROOT / "config" / "pilot_sources.yaml").open(encoding="utf-8") as handle:
        pilot = yaml.safe_load(handle)
    sources = load_source_groups(str(ROOT / "config" / "source_groups.yaml"))
    assert pilot["sources"]
    missing = [name for name in pilot["sources"] if not get_source_metadata(name, sources)]
    assert not missing, f"Pilot sources missing from source_groups.yaml: {missing}"
