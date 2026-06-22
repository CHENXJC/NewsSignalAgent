# Scoring Logic

## Final signal score

Each article receives seven 0-100 components:

`weighted score = sum(component score * configured component weight)`

`final signal score = min(100, weighted score * source group multiplier * source adjustment)`

The components are relevance, urgency, business impact, policy narrative importance, cross-source confirmation, source strength, and novelty. Weights live in `config/scoring_config.yaml`.

## Narrative gap score

`narrative_gap_score` is separate from `final_signal_score`. It evaluates a topic comparison rather than an individual article:

- Region coverage: 10 points per covered region, capped at 40
- Frame diversity: 15 points per additional dominant frame, capped at 30
- Signal strength: 25% of the topic's average final signal score, capped at 25
- Practical implication: 5 points for a recognized substantive gap type

The result is capped from 0 to 100. A high value means the topic has broad coverage, meaningfully different source-group emphasis, and strong underlying signals. It does not mean one framing is correct.

## Limitations

Keyword rules can miss nuance, sarcasm, multilingual equivalence, rewritten duplicates, recency context, and true novelty. Topic normalization and frame assignment are heuristic. Scores prioritize review and do not predict outcomes.

## Future enhancement

A later phase can add optional OpenAI structured analysis with schemas, cited evidence, uncertainty, counter-signals, evaluation examples, and human review. Deterministic fallbacks should remain available.
