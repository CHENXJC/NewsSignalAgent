# Project Status

Current checkpoint: **NEWS-007B-COMPLETE - Local Git Author Config and Public Showcase Commit**

## Completed milestones

- NEWS-002: source architecture, original demo data, Signal Score MVP, dashboard, tests, and documentation
- NEWS-003: optional RSS/API adapters, caching, fetch status, and demo/live/hybrid modes
- NEWS-004: bounded six-source public RSS pilot, health checks, attribution, and safety report
- NEWS-005: neutral Narrative Gap Detector, topic-region matrix, and report export
- NEWS-006: dashboard polish, public README, showcase notes, release checklist, and safety tooling
- NEWS-007: eight real dashboard screenshots, screenshot/README validators, GitHub release guide, and local Git preparation
- NEWS-007B: repository-local Git identity, final safety validation, and local public showcase commit

## Screenshot status

All eight required PNG files exist under `portfolio/showcase_screenshots/`, are non-empty, and match README image references. They were captured from the real localhost dashboard in Hybrid Demo + Live mode; no placeholder or fabricated image was used.

## Git and safety status

Git is initialized locally on `main` with repository-local author `CHENXJC <chenxjc@users.noreply.github.com>`. The public showcase commit was created as `e7a2983`; no global Git identity was changed, no remote exists, and no push was performed. Runtime RSS cache JSON, generated reports/exports, logs, `.env`, virtual environments, and Python caches remain ignored and untracked.

## Run and validate

```powershell
Set-Location F:\AIProjects\NewsSignalAgent
python -m pip install -r requirements.txt
python -m pytest
python -m compileall .
python tools/public_release_check.py
python tools/validate_showcase_screenshots.py
python tools/validate_readme_assets.py
python -m streamlit run app.py
```

## Known limitations

Rule-based analysis is mainly English-focused; live China sources remain disabled; the RSS pilot is deliberately small; source availability can change; outputs are not financial or political advice.

## Next action required

Continue to NEWS-008 for the explicitly authorized GitHub remote/push, online README screenshot verification, About/topics setup, and optional profile pin.
