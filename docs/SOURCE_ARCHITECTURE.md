# Source Architecture

## Why sources are grouped

Grouping separates the role a source plays from the individual publisher. It supports regional comparison, visible weighting, and future adapter selection without coupling ingestion to analysis.

## Regional roles

The **China policy** group captures official narrative and policy direction. `cctv_xinwen_lianbo` is a policy anchor, not an assertion of objective truth; its higher weight represents narrative importance. China business sources add company and market context.

The **Australia public** and **Australia business** groups focus on local policy, household conditions, the RBA, employment, and small-business implications. **US wire** supports broad confirmation, **US business/tech** tracks technology and enterprise adoption, and **global cross-check** provides another regional lens.

## Weighting

Each source has a default weight and each group has a scoring multiplier. Both are explicit configuration assumptions, not editorial truth rankings.

## RSS/API adapter design

NEWS-003 introduced generic adapters only where publisher terms permit. The RSS adapter reads feed metadata; the API adapter is a conservative placeholder for explicitly configured JSON endpoints. Neither retrieves full article bodies.

Each source may define `feed_url`, `api_url`, `enabled`, `fetch_priority`, and `fetch_limit`. Missing values are valid. Disabled and demo-only sources are skipped, while enabled sources without a matching URL receive a visible `no_url` status.

Successful records are stored in per-source JSON files under `cache/rss/`. Fresh cache can avoid a network request; stale cache can serve as fallback after failure. Corrupt cache is treated as empty. Live fetching remains optional because the dashboard must operate offline and source availability or terms can change.

## Compliance boundaries

Do not bypass paywalls, scrape restricted pages, copy full copyrighted articles, collect private content, or commit credentials. An access mode describes adapter intent and does not claim permission or availability. Verify every official URL before enabling it.

## NEWS-004 pilot architecture

`config/pilot_sources.yaml` defines a deliberately small subset, a default per-source limit, and a 40-item total cap. The live manager filters the source universe to this list before requests. NEWS-004 enables SBS News, Guardian Australia, PBS NewsHour, NPR News, TechCrunch, and BBC World after local HTTP and feed-parse checks.

`verified_status` records evidence such as `verified_official`, `verified_public`, or `disabled_no_stable_feed`; it is not a permanent guarantee. `content_capture_policy` constrains ingestion to `title_summary_link_only`, `title_link_only`, or `disabled`. Every live row carries both values alongside source, group, region, URL, publication time, and fetch time.

The bounded health checker reports status without storing response bodies. Its result is operational evidence at one point in time, not an endorsement or promise of future availability.
