"""Neutral, rule-based cross-region framing comparison for NEWS-005."""
from collections import Counter
from datetime import datetime
import re
import pandas as pd

FRAMES = ["Policy / Regulation Frame", "Market / Investment Frame", "Business Opportunity Frame",
          "Consumer Impact Frame", "Technology Innovation Frame", "Social Risk Frame",
          "Geopolitical / Global Risk Frame", "Local Community Frame", "Other Frame"]
REGIONS = ["China", "Australia", "United States", "Global / Other"]
MATRIX_COLUMNS = ["normalized_topic", "region_bucket", "article_count", "avg_signal_score", "top_sources",
                  "dominant_frames", "top_keywords", "representative_titles"]
GAP_COLUMNS = ["normalized_topic", "regions_present", "article_count", "china_frame", "australia_frame",
               "us_frame", "global_frame", "dominant_gap_type", "narrative_gap_score", "business_signal",
               "risk_signal", "content_angle", "suggested_action", "representative_titles"]

TOPIC_RULES = [
    ("AI & Automation", ["artificial intelligence", "automation", "robot", " ai "]),
    ("Interest Rates", ["interest rate", "central bank", " rba ", "rate outlook", "borrowing cost"]),
    ("Cost of Living", ["cost of living", "living cost", "household budget", "price pressure"]),
    ("Housing", ["housing", "home buyer", "rent", "mortgage"]),
    ("Small Business", ["small business", "small companies", "sme", "retailer"]),
    ("Technology Market", ["technology market", "technology firm", "software", "digital infrastructure"]),
    ("Global Trade", ["global trade", "export", "import", "supply chain", "tariff"]),
    ("Energy Transition", ["energy transition", "renewable", "grid", "climate"]),
    ("Education & Student Jobs", ["student job", "students", "graduate hiring", "education", "skills"]),
    ("Consumer Trends", ["consumer trend", "consumer", "household demand", "retail demand"]),
    ("Platform Economy", ["platform economy", "platform seller", "marketplace"]),
    ("Economy & Inflation", ["economy", "economic", "inflation", "growth", "employment"]),
]

STOPWORDS = {"the", "and", "for", "with", "that", "from", "this", "into", "amid", "are", "its", "how",
             "news", "new", "more", "than", "while", "after", "over", "their", "they", "about", "report"}


def _clean(value) -> str:
    return "" if value is None or pd.isna(value) else str(value)


def _row_text(row: pd.Series) -> str:
    return " ".join(_clean(row.get(key, "")) for key in ("title", "summary", "topic", "tags")).lower()


def normalize_topic_label(text: str) -> str:
    padded = f" {_clean(text).lower()} "
    for label, keywords in TOPIC_RULES:
        if any(keyword in padded for keyword in keywords):
            return label
    return "Other"


def assign_narrative_frame(row: pd.Series) -> str:
    text = _row_text(row)
    group = _clean(row.get("source_group", "")).lower()
    rules = [
        ("Policy / Regulation Frame", ["policy", "regulation", "government", "official", "guidance", "rba", "governance"]),
        ("Geopolitical / Global Risk Frame", ["geopolitical", "war", "global risk", "trade uncertainty", "sanction", "diplomatic"]),
        ("Business Opportunity Frame", ["business opportunity", "small business", "service opportunity", "startup", "productivity gain"]),
        ("Technology Innovation Frame", [" ai ", "automation", "technology", "robot", "software", "innovation"]),
        ("Consumer Impact Frame", ["consumer", "household", "cost of living", "housing affordability", "borrower", "rent"]),
        ("Social Risk Frame", ["job loss", "safety", "inequality", "scam", "harm", "unemployment"]),
        ("Local Community Frame", ["local", "community", "student", "city", "regional"]),
        ("Market / Investment Frame", ["market", "investment", "inflation", "interest rate", "trade", "company", "capital"]),
    ]
    if group == "china_policy" and any(word in text for word in ("policy", "official", "guidance", "plan")):
        return "Policy / Regulation Frame"
    return next((frame for frame, terms in rules if any(term in f" {text} " for term in terms)), "Other Frame")


def _region(row: pd.Series) -> str:
    group = _clean(row.get("source_group", "")).lower()
    mapping = {"china_policy": "China", "china_business": "China", "australia_public": "Australia",
               "australia_business": "Australia", "us_wire": "United States",
               "us_business_tech": "United States", "global_cross_check": "Global / Other"}
    if group in mapping:
        return mapping[group]
    raw = _clean(row.get("country_or_region", "")).lower()
    if "china" in raw: return "China"
    if "australia" in raw: return "Australia"
    if raw in {"us", "usa", "united states"}: return "United States"
    return "Global / Other"


def _keywords(series: pd.Series, limit: int = 6) -> str:
    words = re.findall(r"[a-z][a-z-]{2,}", " ".join(series.fillna("").astype(str)).lower())
    counts = Counter(word for word in words if word not in STOPWORDS)
    return ", ".join(word for word, _ in counts.most_common(limit))


def _top_values(series: pd.Series, limit: int = 3) -> str:
    return ", ".join(str(value) for value in series.dropna().astype(str).value_counts().head(limit).index)


def _prepared(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    if result.empty:
        return result
    result["normalized_topic"] = result.apply(lambda row: normalize_topic_label(_row_text(row)), axis=1)
    result["region_bucket"] = result.apply(_region, axis=1)
    result["narrative_frame"] = result.apply(assign_narrative_frame, axis=1)
    if "final_signal_score" not in result:
        result["final_signal_score"] = 0.0
    result["final_signal_score"] = pd.to_numeric(result["final_signal_score"], errors="coerce").fillna(0).clip(0, 100)
    return result


def build_topic_region_matrix(df: pd.DataFrame) -> pd.DataFrame:
    data = _prepared(df)
    if data.empty:
        return pd.DataFrame(columns=MATRIX_COLUMNS)
    rows = []
    for (topic, region), group in data.groupby(["normalized_topic", "region_bucket"], sort=True):
        rows.append({"normalized_topic": topic, "region_bucket": region, "article_count": len(group),
                     "avg_signal_score": round(float(group["final_signal_score"].mean()), 2),
                     "top_sources": _top_values(group.get("source", pd.Series(dtype=str))),
                     "dominant_frames": _top_values(group["narrative_frame"], 2),
                     "top_keywords": _keywords(group.get("title", pd.Series(dtype=str))),
                     "representative_titles": " | ".join(group.get("title", pd.Series(dtype=str)).dropna().astype(str).head(3))})
    return pd.DataFrame(rows, columns=MATRIX_COLUMNS)


def _gap_type(frames: set[str], regions: list[str]) -> str:
    if {"Policy / Regulation Frame", "Market / Investment Frame"}.issubset(frames): return "Policy vs Market"
    if {"Consumer Impact Frame", "Business Opportunity Frame"}.issubset(frames): return "Consumer Pain vs Business Opportunity"
    if {"Technology Innovation Frame", "Social Risk Frame"}.issubset(frames): return "Technology Optimism vs Social Risk"
    if "Local Community Frame" in frames and ("Market / Investment Frame" in frames or "Global / Other" in regions): return "Local Impact vs Global Market"
    if len(frames) == 1: return "Low Gap / Similar Framing"
    if len(regions) >= 3 and len(frames) >= 2: return "National Priority Difference"
    return "Other Gap"


def _signals(topic: str, gap_type: str) -> tuple[str, str, str, str]:
    business = f"Compare how {topic.lower()} changes customer needs, operating costs, or timing across covered regions."
    risk = f"A {gap_type.lower()} may cause teams to overgeneralize one region's assumptions to another."
    angle = f"Create a neutral '{topic} across regions' brief showing emphasis, omissions, and practical implications."
    action = "Validate the strongest difference against original sources, then test one region-specific decision or content hypothesis."
    return business, risk, angle, action


def detect_narrative_gaps(df: pd.DataFrame) -> pd.DataFrame:
    data = _prepared(df)
    if data.empty:
        return pd.DataFrame(columns=GAP_COLUMNS)
    rows = []
    for topic, group in data.groupby("normalized_topic", sort=True):
        regions = [region for region in REGIONS if region in set(group["region_bucket"])]
        if len(regions) < 2:
            continue
        frames_by_region = {region: _top_values(region_df["narrative_frame"], 1) for region, region_df in group.groupby("region_bucket")}
        distinct_frames = {frame for frame in frames_by_region.values() if frame}
        gap_type = _gap_type(distinct_frames, regions)
        avg_score = float(group["final_signal_score"].mean())
        coverage_points = min(40, len(regions) * 10)
        diversity_points = min(30, max(0, len(distinct_frames) - 1) * 15)
        signal_points = min(25, avg_score * 0.25)
        implication_points = 5 if gap_type not in {"Low Gap / Similar Framing", "Other Gap"} else 0
        score = round(max(0, min(100, coverage_points + diversity_points + signal_points + implication_points)), 2)
        business, risk, angle, action = _signals(topic, gap_type)
        title_parts = []
        for region in regions:
            titles = group[group["region_bucket"] == region].get("title", pd.Series(dtype=str)).dropna().astype(str).head(2)
            title_parts.append(f"{region}: {' | '.join(titles)}")
        rows.append({"normalized_topic": topic, "regions_present": ", ".join(regions), "article_count": len(group),
                     "china_frame": frames_by_region.get("China", ""), "australia_frame": frames_by_region.get("Australia", ""),
                     "us_frame": frames_by_region.get("United States", ""), "global_frame": frames_by_region.get("Global / Other", ""),
                     "dominant_gap_type": gap_type, "narrative_gap_score": score, "business_signal": business,
                     "risk_signal": risk, "content_angle": angle, "suggested_action": action,
                     "representative_titles": " || ".join(title_parts)})
    return pd.DataFrame(rows, columns=GAP_COLUMNS).sort_values("narrative_gap_score", ascending=False).reset_index(drop=True)


def generate_gap_explanation(row: pd.Series) -> str:
    return (f"{row.get('normalized_topic', 'This topic')} appears across {row.get('regions_present', 'multiple regions')}. "
            f"The main framing difference is {row.get('dominant_gap_type', 'Other Gap')}. "
            f"This matters because regional emphasis can change business, market, risk, and content decisions. "
            f"Suggested use: {row.get('suggested_action', '')}")


def generate_gap_report(df: pd.DataFrame, top_n: int = 10) -> str:
    gaps = detect_narrative_gaps(df)
    generated = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    lines = ["# NewsSignalAgent Narrative Gap Report", "", f"Generated: {generated}", "",
             "Methodology: transparent keyword topic normalization and source-group framing comparison. Scores prioritize coverage, frame difference, signal strength, and practical implications.", "",
             "## Top Narrative Gaps", "", "| Score | Topic | Regions | Gap type |", "|---:|---|---|---|"]
    for _, row in gaps.head(top_n).iterrows():
        lines.append(f"| {row['narrative_gap_score']:.2f} | {row['normalized_topic']} | {row['regions_present']} | {row['dominant_gap_type']} |")
    lines.extend(["", "## Region Comparison Summary", ""])
    for _, row in gaps.head(top_n).iterrows():
        lines.append(f"### {row['normalized_topic']}")
        lines.append(generate_gap_explanation(row))
        lines.extend([f"- Business opportunity: {row['business_signal']}", f"- Risk: {row['risk_signal']}", f"- Content angle: {row['content_angle']}", ""])
    lines.extend(["---", "Neutral framing comparison only. This report does not judge truth or political merit and is not financial or political advice. Verify original sources."])
    return "\n".join(lines)
