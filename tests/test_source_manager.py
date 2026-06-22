from pathlib import Path
import yaml
from modules.source_manager import get_source_group_weight, get_source_metadata, load_source_groups

ROOT = Path(__file__).parents[1]


def test_source_config_and_anchor():
    config = load_source_groups(str(ROOT / "config" / "source_groups.yaml"))
    anchor = get_source_metadata("cctv_xinwen_lianbo", config)
    assert anchor["source_type"] == "policy_anchor"


def test_china_policy_weight_available():
    with (ROOT / "config" / "scoring_config.yaml").open(encoding="utf-8") as handle:
        scoring = yaml.safe_load(handle)
    assert get_source_group_weight("china_policy", scoring) == 1.30
