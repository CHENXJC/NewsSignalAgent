"""Rule-based signal scoring for the NEWS-002 demo."""
import pandas as pd
from modules.source_manager import get_source_group_weight, get_source_metadata

HIGH_RELEVANCE = ["ai", "automation", "interest rate", "rba", "inflation", "policy", "small business", "housing", "jobs", "trade"]


def _text(row: pd.Series) -> str:
    return " ".join("" if pd.isna(row.get(k, "")) else str(row.get(k, "")) for k in ("title", "summary", "topic", "tags")).lower()


def _component_scores(row: pd.Series, cross_country_count: int = 1) -> dict:
    text, group, source = _text(row), str(row.get("source_group", "")), str(row.get("source", ""))
    relevance = min(95, 55 + 8 * sum(term in text for term in HIGH_RELEVANCE))
    urgency = 82 if any(k in text for k in ("urgent", "rate", "inflation", "risk", "policy")) else 62
    business = 88 if any(k in text for k in ("business", "automation", "consumer", "export", "investment", "service opportun")) else 65
    policy = 92 if source == "cctv_xinwen_lianbo" else (84 if group == "china_policy" else (72 if "policy" in text else 50))
    cross_source = min(90, 50 + max(0, cross_country_count - 1) * 20)
    strength = 86 if group in {"us_wire", "global_cross_check"} else (80 if source == "cctv_xinwen_lianbo" else 70)
    return {"relevance_score": relevance, "urgency_score": urgency, "business_impact_score": business,
            "policy_narrative_score": policy, "cross_source_score": cross_source,
            "source_strength_score": strength, "novelty_score": 70}


def calculate_signal_score(row: pd.Series, scoring_config: dict, source_config: dict) -> float:
    cross_count = row.get("_cross_country_count", 1)
    cross_count = 1 if pd.isna(cross_count) else int(cross_count)
    scores = _component_scores(row, cross_count)
    weights = scoring_config.get("signal_score_weights", {})
    mapping = {"relevance": "relevance_score", "urgency": "urgency_score", "business_impact": "business_impact_score",
               "policy_narrative_importance": "policy_narrative_score", "cross_source_confirmation": "cross_source_score",
               "source_strength": "source_strength_score", "novelty": "novelty_score"}
    weighted = sum(scores[column] * float(weights.get(key, 0)) for key, column in mapping.items())
    group_multiplier = get_source_group_weight(str(row.get("source_group", "")), scoring_config)
    metadata = get_source_metadata(str(row.get("source", "")), source_config)
    source_weight = float(metadata.get("default_weight", 1.0))
    return round(max(0.0, min(100.0, weighted * group_multiplier * (0.85 + 0.15 * source_weight))), 2)


def score_news_dataframe(df: pd.DataFrame, scoring_config: dict, source_config: dict) -> pd.DataFrame:
    result = df.copy()
    component_columns = ["relevance_score", "urgency_score", "business_impact_score", "policy_narrative_score",
                         "cross_source_score", "source_strength_score", "novelty_score"]
    if result.empty:
        for column in component_columns:
            result[column] = pd.Series(dtype="float64")
        result["source_group_multiplier"] = pd.Series(dtype="float64")
        result["final_signal_score"] = pd.Series(dtype="float64")
        return result
    for column in ("topic", "country_or_region", "source_group", "source"):
        if column not in result:
            result[column] = ""
        result[column] = result[column].fillna("")
    topic_counts = result.groupby("topic")["country_or_region"].transform("nunique")
    result["_cross_country_count"] = topic_counts
    components = result.apply(lambda row: pd.Series(_component_scores(row, int(row["_cross_country_count"]))), axis=1)
    result = pd.concat([result, components], axis=1)
    result["source_group_multiplier"] = result["source_group"].map(lambda group: get_source_group_weight(group, scoring_config))
    result["final_signal_score"] = result.apply(lambda row: calculate_signal_score(row, scoring_config, source_config), axis=1)
    return result.drop(columns=["_cross_country_count"]).sort_values("final_signal_score", ascending=False).reset_index(drop=True)
