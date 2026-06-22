from pathlib import Path
from tools.validate_showcase_screenshots import REQUIRED_SCREENSHOTS, validate_showcase_screenshots

ROOT = Path(__file__).parents[1]


def test_screenshot_validator_is_structured_and_lists_required_files():
    result = validate_showcase_screenshots(str(ROOT))
    assert isinstance(result, dict)
    assert result["required"] == REQUIRED_SCREENSHOTS
    assert set(REQUIRED_SCREENSHOTS).issubset(set(result["existing"] + result["missing"]))
