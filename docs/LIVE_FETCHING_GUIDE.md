# Live Fetching Guide

Live fetching is optional. The application defaults to local Demo Data and stays usable without internet.

## NEWS-004 pilot source config

`config/pilot_sources.yaml` is the default live scope. It lists only six verified pilot sources and limits total items. Select **All Enabled Sources** only when intentionally validating broader configuration. A source must exist in `source_groups.yaml`, be enabled, have a matching access mode, and provide a feed URL.

## Enable an official source

1. Verify the publisher provides the RSS/API endpoint and permits its use.
2. Find the source in `config/source_groups.yaml`.
3. Set an `access_mode` containing `rss` or `api`.
4. Add the verified `feed_url` or `api_url`.
5. Set `enabled: true` and a conservative `fetch_limit`.
6. Choose **Live Sources** in the dashboard and inspect **Fetch Status**.

If an API requires a key, configure only its environment-variable name using `api_key_env`; keep the actual value in the environment or Git-ignored `.env`. Set `enabled: false` to stop requests. Missing URLs are accepted and produce `no_url` when otherwise enabled.

## Cache behavior

Successful normalized responses are saved as `cache/rss/<source>.json` with a UTC timestamp. Fresh cache can avoid a request. Existing stale cache may be used if a live request returns no usable records. Generated JSON is excluded from Git.

Use **Refresh live sources** to bypass fresh-cache reuse for that run. Adjust maximum cache age in the sidebar.

## Troubleshooting

- `disabled`: enable only after verification.
- `no_url`: add the correct official URL for the selected access mode.
- `failed`: check connectivity, endpoint format, availability, and terms.
- `cache_used`: cache avoided a request or provided fallback.
- No rows: use Demo or Hybrid mode while reviewing configuration.
- TLS failure on Windows: keep verification enabled and install `truststore` so Python uses the system certificate store.

## Health checks

Open **Fetch Status** and select **Run source health check**. The bounded checker reports HTTP status, parseability, entry count, verification metadata, and timestamp for the pilot list. A healthy result can later become a warning or failure when a publisher changes its feed.

## Do not

- Add paywalled full-text scrapers or bypass access controls.
- Add private credentials to code, YAML, logs, or cache.
- Upload `.env`.
- Store copyrighted full article text; retain only permitted metadata and short descriptions.
