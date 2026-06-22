from pathlib import Path
from tools.public_release_check import run_public_release_check


def test_public_release_check_returns_structured_result(tmp_path):
    (tmp_path / "README.md").write_text("# Example", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "portfolio" / "showcase_screenshots").mkdir(parents=True)
    result = run_public_release_check(str(tmp_path))
    assert {"project_root", "checks", "summary", "safe_to_continue"}.issubset(result)
    assert isinstance(result["checks"], list)
    assert result["safe_to_continue"] is True


def test_public_release_check_flags_env(tmp_path):
    key_name = "OPENAI" + "_API_KEY"
    (tmp_path / ".env").write_text(f"{key_name}=example-not-a-real-key", encoding="utf-8")
    result = run_public_release_check(str(tmp_path))
    assert result["summary"]["FAIL"] >= 1
