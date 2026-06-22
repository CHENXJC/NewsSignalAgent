"""Rule-based, human-readable demo insights."""
import pandas as pd


def generate_basic_insight(row: pd.Series) -> str:
    signal = row.get("signal_type", "News Signal")
    return (f"What happened: {row.get('summary', '')} Why it matters: this {row.get('topic', 'topic').lower()} development "
            f"may affect decisions in {row.get('region_bucket', row.get('country_or_region', 'the market'))}. "
            f"Signal: {signal} with a demo score of {float(row.get('final_signal_score', 0)):.1f}/100.")


def generate_action_suggestion(row: pd.Series) -> str:
    signal = str(row.get("signal_type", ""))
    if signal == "Business Opportunity":
        return "Validate the affected customer problem and test a small, measurable offer before investing further."
    if signal == "Policy Signal":
        return "Track the next official update and map which industries, audiences, or compliance choices may be affected."
    if signal == "Technology Trend":
        return "Compare the workflow against current costs and run a supervised pilot with a clear success metric."
    if signal == "Global Risk Signal":
        return "Cross-check original sources and prepare a low-cost contingency for the most exposed assumption."
    return "Cross-check the source, watch for confirmation, and turn the signal into one testable research question."
