# Narrative Gap Detector

## Purpose

The detector compares how source groups in different regions frame the same broad topic. It identifies emphasis, omissions, and practical differences that can support business research, risk awareness, market context, and content planning.

## What it does

1. Normalizes article text into broad comparison topics.
2. Assigns a transparent keyword-based narrative frame.
3. Aggregates topic coverage, average signal score, sources, keywords, frames, and representative titles by region.
4. Detects topics covered in at least two regions.
5. Produces gap type, score, business signal, risk signal, content angle, and suggested action.

It does **not** decide which source is right, truthful, politically preferable, or more legitimate. It does not infer intent and does not replace reading original sources.

## Frame categories

- Policy / Regulation
- Market / Investment
- Business Opportunity
- Consumer Impact
- Technology Innovation
- Social Risk
- Geopolitical / Global Risk
- Local Community
- Other

## Gap types

- Policy vs Market
- Local Impact vs Global Market
- Consumer Pain vs Business Opportunity
- Technology Optimism vs Social Risk
- National Priority Difference
- Low Gap / Similar Framing
- Other Gap

## Scoring logic

The 0-100 score adds region coverage (up to 40), dominant-frame diversity (up to 30), 25% of average article signal score (up to 25), and a 5-point practical-implication bonus for recognized gap types. All inputs remain inspectable in the matrix and gap table.

## Example output

An AI & Automation topic may appear as a policy/regulation frame in China, a small-business opportunity frame in Australia, and a technology/market frame in the United States. The detector can suggest validating region-specific adoption assumptions and creating a neutral comparison brief.

## Limitations

Rules are English-focused, keyword order affects classification, a dominant frame compresses internal diversity, and absent coverage may reflect the small dataset rather than genuine silence. Demo China coverage and live Western feeds are not a balanced research sample. Scores are prioritization aids, not forecasts.

## Future structured analysis

An optional OpenAI layer could later return schema-validated frames, evidence snippets, uncertainty, counter-framings, and multilingual topic equivalence. It should preserve source links, deterministic fallback, evaluation sets, and human review.
