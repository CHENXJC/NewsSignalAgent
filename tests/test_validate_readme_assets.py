from pathlib import Path
from tools.validate_readme_assets import validate_readme_assets

ROOT = Path(__file__).parents[1]


def test_readme_asset_validator_scans_readme():
    result = validate_readme_assets(str(ROOT))
    assert isinstance(result, dict)
    assert result["references"]
    assert result["readme"].endswith("README.md")
