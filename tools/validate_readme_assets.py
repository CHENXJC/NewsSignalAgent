"""Validate local Markdown image references in README.md."""
from pathlib import Path
import re

IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def validate_readme_assets(project_root: str) -> dict:
    root = Path(project_root).resolve()
    readme = root / "README.md"
    if not readme.is_file():
        return {"readme": str(readme), "references": [], "existing": [], "missing": [],
                "results": [{"level": "FAIL", "path": None, "message": "README.md is missing."}],
                "summary": {"PASS": 0, "WARNING": 0, "FAIL": 1}}
    references = []
    for raw in IMAGE_PATTERN.findall(readme.read_text(encoding="utf-8")):
        path_text = raw.strip().split()[0].strip("<>")
        if path_text.startswith(("http://", "https://", "data:")):
            continue
        references.append(path_text)
    results, existing, missing = [], [], []
    for ref in references:
        path = root / ref
        if path.is_file() and path.stat().st_size > 0:
            existing.append(ref)
            results.append({"level": "PASS", "path": ref, "message": "Local image exists and is non-empty."})
        else:
            missing.append(ref)
            results.append({"level": "WARNING", "path": ref, "message": "Referenced local image is missing or empty."})
    counts = {level: sum(item["level"] == level for item in results) for level in ("PASS", "WARNING", "FAIL")}
    return {"readme": str(readme), "references": references, "existing": existing, "missing": missing,
            "results": results, "summary": counts}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    report = validate_readme_assets(str(root))
    print("NewsSignalAgent README Asset Validation")
    for item in report["results"]:
        print(f"[{item['level']}] {item.get('path') or 'README'}: {item['message']}")
    print("References:", len(report["references"]))
    print("Missing:", ", ".join(report["missing"]) or "None")
    s = report["summary"]
    print(f"Summary: {s['PASS']} PASS / {s['WARNING']} WARNING / {s['FAIL']} FAIL")
    return 1 if s["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
