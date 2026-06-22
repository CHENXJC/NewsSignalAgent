"""Read-only public release safety checks for NewsSignalAgent."""
from __future__ import annotations
from pathlib import Path
import re
import subprocess
from typing import Iterable
try:
    from tools.validate_readme_assets import validate_readme_assets
    from tools.validate_showcase_screenshots import validate_showcase_screenshots
except ModuleNotFoundError:  # Direct execution sets tools/ as sys.path[0].
    from validate_readme_assets import validate_readme_assets
    from validate_showcase_screenshots import validate_showcase_screenshots

TEXT_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".json", ".csv", ".txt", ".toml", ".ini", ".example"}
SKIP_PARTS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}


def _result(level: str, check: str, message: str) -> dict:
    return {"level": level, "check": check, "message": message}


def _text_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {".env", ".env.example", ".gitignore"}:
            yield path


def _secret_hits(root: Path) -> list[str]:
    patterns = [
        re.compile(r"(?:OPENAI_API_KEY|NEWS_API_KEY)[ \t]*=[ \t]*['\"]?([^\s'\"]+)", re.I),
        re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
        re.compile(r"\bxoxb-[A-Za-z0-9-]{20,}\b"),
        re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35,}\b"),
    ]
    hits = []
    this_file = Path(__file__).resolve()
    for path in _text_files(root):
        if path.resolve() == this_file:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if any(pattern.search(text) for pattern in patterns):
            hits.append(str(path.relative_to(root)))
    return sorted(set(hits))


def run_public_release_check(project_root: str) -> dict:
    root = Path(project_root).resolve()
    checks = []
    env_files = [path for path in root.glob(".env*") if path.name != ".env.example"]
    checks.append(_result("FAIL" if env_files else "PASS", "Local environment file",
                          f"Found: {', '.join(path.name for path in env_files)}" if env_files else "No publishable .env file found."))

    secret_hits = _secret_hits(root)
    checks.append(_result("FAIL" if secret_hits else "PASS", "Secret-pattern scan",
                          f"Potential secrets in: {', '.join(secret_hits)}" if secret_hits else "No populated key or token patterns detected."))

    artifacts = [
        ("RSS cache", root / "cache" / "rss", "*.json"),
        ("Generated reports", root / "outputs" / "reports", "*.md"),
        ("Generated exports", root / "outputs" / "exports", "*.csv"),
    ]
    for label, folder, pattern in artifacts:
        found = list(folder.glob(pattern)) if folder.exists() else []
        checks.append(_result("WARNING" if found else "PASS", label,
                              f"{len(found)} local generated file(s) found; confirm they remain Git-ignored and safe." if found else "No generated files found."))

    screenshot_report = validate_showcase_screenshots(str(root))
    screenshot_level = "FAIL" if screenshot_report["summary"]["FAIL"] else "WARNING" if screenshot_report["missing"] else "PASS"
    checks.append(_result(screenshot_level, "Showcase screenshots",
                          f"{len(screenshot_report['existing'])}/8 required PNG files exist; missing: {', '.join(screenshot_report['missing']) or 'none'}."))

    asset_report = validate_readme_assets(str(root))
    asset_level = "FAIL" if asset_report["summary"]["FAIL"] else "WARNING" if asset_report["missing"] else "PASS"
    checks.append(_result(asset_level, "README image assets",
                          f"{len(asset_report['existing'])}/{len(asset_report['references'])} local image references resolve; missing: {', '.join(asset_report['missing']) or 'none'}."))

    required_ignores = [".env", "cache/rss/*.json", "logs/*.log", "outputs/reports/*.md", "outputs/exports/*.csv"]
    gitignore = root / ".gitignore"
    ignore_text = gitignore.read_text(encoding="utf-8") if gitignore.is_file() else ""
    missing_ignores = [pattern for pattern in required_ignores if pattern not in ignore_text]
    checks.append(_result("WARNING" if missing_ignores else "PASS", "Runtime ignore rules",
                          f"Missing ignore rules: {', '.join(missing_ignores)}" if missing_ignores else "Required runtime artifact patterns are ignored."))

    git_dir = root / ".git"
    if git_dir.is_dir():
        status = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True, check=False)
        dirty_count = len([line for line in status.stdout.splitlines() if line.strip()])
        checks.append(_result("WARNING" if dirty_count else "PASS", "Git working tree",
                              f"Git is initialized with {dirty_count} pending path(s)." if dirty_count else "Git is initialized and the working tree is clean."))
        tracked = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=False).stdout.splitlines()
        unsafe = [path for path in tracked if path == ".env" or path.startswith(".venv/") or "__pycache__/" in path
                  or (path.startswith("cache/rss/") and path.endswith(".json"))
                  or (path.startswith("logs/") and path.endswith(".log"))
                  or (path.startswith("outputs/reports/") and path.endswith(".md"))
                  or (path.startswith("outputs/exports/") and path.endswith(".csv"))]
        checks.append(_result("FAIL" if unsafe else "PASS", "Tracked runtime artifacts",
                              f"Unsafe tracked paths: {', '.join(unsafe)}" if unsafe else "No ignored runtime artifacts are tracked."))
    else:
        checks.append(_result("WARNING", "Git working tree", "Git is not initialized yet."))
    checks.append(_result("PASS" if (root / "README.md").is_file() else "FAIL", "README", "README.md exists." if (root / "README.md").is_file() else "README.md is missing."))
    checks.append(_result("PASS" if (root / "tests").is_dir() else "FAIL", "Tests", "tests directory exists." if (root / "tests").is_dir() else "tests directory is missing."))

    counts = {level: sum(item["level"] == level for item in checks) for level in ("PASS", "WARNING", "FAIL")}
    return {"project_root": str(root), "checks": checks, "summary": counts, "safe_to_continue": counts["FAIL"] == 0}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    report = run_public_release_check(str(root))
    print("NewsSignalAgent Public Release Check")
    print(f"Project: {report['project_root']}")
    for item in report["checks"]:
        print(f"[{item['level']}] {item['check']}: {item['message']}")
    summary = report["summary"]
    print(f"Summary: {summary['PASS']} PASS / {summary['WARNING']} WARNING / {summary['FAIL']} FAIL")
    return 0 if report["safe_to_continue"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
