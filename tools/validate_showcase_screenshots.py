"""Validate the NEWS-007 screenshot pack without modifying files."""
from pathlib import Path

REQUIRED_SCREENSHOTS = [
    "01_home_overview.png", "02_global_signal_overview.png", "03_china_policy_signal.png",
    "04_cross_country_comparison.png", "05_narrative_gap_detector.png",
    "06_fetch_status_live_pilot.png", "07_source_architecture.png", "08_export_report_preview.png",
]


def validate_showcase_screenshots(project_root: str) -> dict:
    root = Path(project_root).resolve()
    folder = root / "portfolio" / "showcase_screenshots"
    results, existing, missing = [], [], []
    if not folder.is_dir():
        results.append({"level": "FAIL", "file": None, "message": "Screenshot folder is missing."})
        missing = REQUIRED_SCREENSHOTS.copy()
    else:
        for name in REQUIRED_SCREENSHOTS:
            path = folder / name
            if not path.exists():
                missing.append(name)
                results.append({"level": "WARNING", "file": name, "message": "Required screenshot is missing."})
            elif path.suffix.lower() != ".png":
                results.append({"level": "FAIL", "file": name, "message": "Screenshot extension must be .png."})
            elif path.stat().st_size == 0:
                results.append({"level": "FAIL", "file": name, "message": "Screenshot file is empty."})
            else:
                existing.append(name)
                results.append({"level": "PASS", "file": name, "message": f"PNG exists ({path.stat().st_size} bytes)."})
    counts = {level: sum(item["level"] == level for item in results) for level in ("PASS", "WARNING", "FAIL")}
    return {"folder": str(folder), "required": REQUIRED_SCREENSHOTS.copy(), "existing": existing,
            "missing": missing, "results": results, "summary": counts}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    report = validate_showcase_screenshots(str(root))
    print("NewsSignalAgent Screenshot Validation")
    for item in report["results"]:
        print(f"[{item['level']}] {item.get('file') or 'folder'}: {item['message']}")
    print("Existing:", ", ".join(report["existing"]) or "None")
    print("Missing:", ", ".join(report["missing"]) or "None")
    s = report["summary"]
    print(f"Summary: {s['PASS']} PASS / {s['WARNING']} WARNING / {s['FAIL']} FAIL")
    return 1 if s["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
