# Public Showcase Manifest

## Safe to publish after review

- `app.py`
- `modules/` and `tools/public_release_check.py`
- Secret-free `config/`
- Original `data/demo_news.csv`
- `docs/` and public showcase notes
- `tests/` and dependency metadata
- Screenshot placeholders and sanitized screenshots
- `.env.example` with empty values only

## Do not publish

- `.env`, API keys, cookies, tokens, paid-source credentials, or private feed URLs
- Raw large-scale article caches or generated live cache JSON
- Unsanitized generated reports and CSV exports
- Copyrighted full article text, paywalled material, or scraped video transcripts
- Private user data, private notes, personal paths, or account information
- Personal investment recommendations or individualized political advice
- Virtual environments, caches, test artifacts, and logs

## Public data rule

Demo content must be original or clearly licensed. Live screenshots should show only short permitted feed metadata with attribution. Every screenshot and report must receive a manual safety review before publication.
