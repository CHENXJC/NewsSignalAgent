"""Explainable keyword-based signal classification."""
import pandas as pd


def _text(row: pd.Series) -> str:
    return " ".join("" if pd.isna(row.get(key, "")) else str(row.get(key, "")) for key in ("title", "summary", "topic", "tags")).lower()


def classify_signal_type(row: pd.Series) -> str:
    text = _text(row)
    rules = [
        ("Policy Signal", ["policy", "guidance", "official", "rba", "governance"]),
        ("Global Risk Signal", ["global risk", "uncertainty", "supply chain", "constraint"]),
        ("Business Opportunity", ["business opportunity", "small business", "service opportunities", "exporter"]),
        ("Technology Trend", ["ai", "automation", "technology", "robotics"]),
        ("Market Signal", ["market", "inflation", "interest rate", "investment", "trade"]),
        ("Social / Consumer Signal", ["consumer", "housing", "student", "living costs", "jobs"]),
        ("Content Idea Signal", ["creator", "short video", "publisher"]),
    ]
    return next((label for label, words in rules if any(word in text for word in words)), "Market Signal")


def assign_region_bucket(row: pd.Series) -> str:
    region = str(row.get("country_or_region", "")).lower()
    if "china" in region:
        return "China"
    if "australia" in region:
        return "Australia"
    if "united states" in region or region in {"us", "usa"}:
        return "United States"
    return "Global"
