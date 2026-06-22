# Official Source Pilot

## Why the pilot is small

NEWS-004 proves the architecture with limited traffic and visible failure handling. It does not attempt comprehensive monitoring. A small set makes provenance, publisher terms, feed stability, and regional balance easier to review.

## Enabled sources

These endpoints returned HTTP 200 and parseable RSS in the local Windows environment on 2026-06-22:

- SBS News - Australia public signal
- Guardian Australia - Australia public/mainstream signal
- PBS NewsHour - US public signal
- NPR News - US public signal
- TechCrunch - US technology trend signal
- BBC World - global cross-check signal

Each captures title, short feed summary, original link, timestamps, and attribution only. Per-source limits are 6-8 items, with a 40-item pilot maximum.

## Disabled candidates

- `cctv_xinwen_lianbo`: remains the policy anchor, but no stable official RSS was confirmed. It is disabled for a future manual/public-page workflow. Video pages are not scraped, downloaded, or transcribed.
- `xinhua`: the supplied legacy English RSS candidate returned HTTP 404. It remains disabled until an official stable endpoint is reconfirmed.
- Other publishers remain disabled because NEWS-004 intentionally avoids expanding the pilot or because access and terms need later review.

## Adding another official source

Verify publisher ownership, endpoint stability, terms, and feed structure. Add verification metadata, choose the narrowest capture policy, keep a conservative limit, test health and failure behavior, then add it to `pilot_sources.yaml` only after review.

## Compliance boundaries

Do not bypass paywalls or access controls, scrape article/video pages, store full copyrighted text, add unofficial feed generators, or place credentials in configuration, cache, logs, or Git. Recheck availability and `verified_status` over time.
