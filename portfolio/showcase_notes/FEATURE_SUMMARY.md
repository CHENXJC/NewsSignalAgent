# Feature Summary

## Core Features

- Demo, bounded Live RSS Pilot, and Hybrid workflows
- Explainable Signal Score and rule-based insight suggestions
- Nine-tab Streamlit dashboard with filters and export controls
- Source health, cache fallback, and per-source status

## Source Architecture

Seven source groups cover China policy/business, Australia public/business, US wire/business-tech, and global cross-check roles. Six public feeds form the NEWS-004 pilot; unstable candidates remain disabled.

## Signal Scoring

Seven 0-100 components combine relevance, urgency, business impact, policy narrative importance, cross-source confirmation, source strength, and novelty. Configured multipliers remain visible and editable.

## Narrative Gap Detector

Shared topics are compared by region and source-group emphasis. Transparent rules identify framing differences and generate business, risk, content, and action hypotheses without political truth judgments.

## Export System

Users can download signal CSV/Markdown and create local live-status or narrative-gap reports. Generated artifacts are Git-ignored by default.

## Compliance-first Design

No paywall bypass, full article-body scraping, credentials, or private data. Live records retain attribution and capture-policy metadata. Demo mode works offline.

## Current Limitations

Rules are mainly English-keyword based, live China feeds remain disabled, the pilot is intentionally small, and feed availability may change.

## Future Roadmap

NEWS-007: reviewed screenshot capture, GitHub repository preparation, and final public safety review.
