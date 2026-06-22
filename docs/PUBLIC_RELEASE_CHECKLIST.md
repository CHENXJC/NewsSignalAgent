# Public Release Checklist

## Secrets and local configuration

- [ ] Run `python tools/public_release_check.py`.
- [ ] Confirm `.env` does not exist in the release set.
- [ ] Confirm no populated `OPENAI_API_KEY`, `NEWS_API_KEY`, `sk-`, `xoxb-`, Telegram token, cookie, or credential is present.
- [ ] Confirm `.env.example` contains placeholders only.

## Cache, reports, and output data

- [ ] Confirm `cache/rss/*.json` remains ignored and untracked.
- [ ] Review generated Markdown reports; do not publish live report content unless sanitized.
- [ ] Confirm `outputs/reports/*.md` and `outputs/exports/*.csv` remain ignored.
- [ ] Confirm no full article bodies, private user data, or large raw datasets are present.

## Copyright and access

- [ ] No paywall bypass, protected-page scraping, unofficial feed generator, or paid-source credential.
- [ ] Demo summaries are original and live records contain only permitted short metadata.
- [ ] Source attribution, URL, verification status, and capture policy are preserved.

## Screenshots

- [ ] Follow `docs/SCREENSHOTS_GUIDE.md` and use reviewed PNG files only.
- [ ] No local username, personal path, terminal, account, token, or private note is visible.
- [ ] Demo/live context and disclaimers are clear.
- [ ] Every README image path resolves before push.
- [ ] Run `python tools/validate_showcase_screenshots.py` and confirm 8 PASS / 0 missing.
- [ ] Run `python tools/validate_readme_assets.py` and confirm every local image resolves.

## README and tests

- [ ] README setup commands work on a clean environment.
- [ ] Screenshot, limitations, compliance, roadmap, and disclaimer sections are current.
- [ ] `python -m pytest` passes.
- [ ] `python -m compileall .` passes.
- [ ] Demo mode loads without internet; Hybrid failure behavior is graceful.

## Before GitHub push

- [ ] Inspect `git status --short` and the complete staged diff.
- [ ] Confirm generated cache/report/export files are not staged.
- [ ] Confirm `.venv`, `.env`, logs, and private notes are not staged.
- [ ] Run the safety script and tests again immediately before push.
- [ ] Push only after explicit user authorization.
- [ ] Use `git ls-files` to confirm `.env`, RSS cache JSON, generated reports/exports, logs, `.venv`, and `__pycache__` are not tracked.
- [ ] Set the GitHub About description and reviewed repository topics from `docs/GITHUB_RELEASE_GUIDE.md`.

## Post-push verification

- [ ] Open the public repository in a signed-out/private browser window.
- [ ] Confirm all eight README images render and contain no private information.
- [ ] Confirm setup commands, links, About description, and topics are correct.
- [ ] Confirm no generated runtime artifacts appear in the repository tree.
