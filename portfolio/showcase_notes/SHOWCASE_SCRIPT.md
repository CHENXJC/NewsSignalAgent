# 60-90 Second Showcase Script

## One-sentence pitch

NewsSignalAgent is a local-first workflow that turns regional news metadata into explainable business, market, policy, risk, and cross-country narrative signals.

## Presentation flow

**Problem:** News volume is high, but summaries alone do not show what deserves attention or how regional emphasis changes the decision context.

**Solution:** NewsSignalAgent loads stable demo data or a bounded six-source RSS pilot, normalizes and scores each signal, then compares topic framing across China, Australia, the United States, and global sources.

**Core workflow:** Source config -> demo/live/hybrid loading -> cleaning and deduplication -> classification and Signal Score -> Narrative Gap Detector -> dashboard and Markdown/CSV exports.

**Key modules:** The fetch manager handles cache and per-source failure; the signal scorer provides transparent prioritization; the narrative detector builds topic-region matrices and practical gap explanations.

**What makes it different:** It is not a generic summarizer. It joins source architecture, operational health, explainable scoring, and neutral cross-country framing comparison in one portfolio workflow.

**Safety boundary:** It does not bypass paywalls, collect full article bodies, require API keys, judge political truth, or replace original sources. Demo mode remains the stable baseline.

**Tech stack:** Python, Streamlit, pandas, PyYAML, feedparser, requests, truststore, and pytest.

**Roadmap:** NEWS-007 will capture the reviewed screenshot pack and prepare the public GitHub repository after a final safety review.
