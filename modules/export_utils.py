"""CSV and Markdown export helpers."""
from datetime import datetime
from pathlib import Path
import pandas as pd


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def export_signals_to_csv(df: pd.DataFrame, output_dir: str) -> str:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / f"news_signals_{_timestamp()}.csv"
    df.to_csv(path, index=False)
    return str(path)


def markdown_report(df: pd.DataFrame, top_n: int = 10) -> str:
    generated = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    lines = ["# NewsSignalAgent Signal Report", "", f"Generated: {generated}", "", "## Top Signals", "",
             "| Score | Region | Topic | Title |", "|---:|---|---|---|"]
    for _, row in df.head(top_n).iterrows():
        title = str(row.get("title", "")).replace("|", "\\|")
        lines.append(f"| {float(row.get('final_signal_score', 0)):.2f} | {row.get('country_or_region', '')} | {row.get('topic', '')} | {title} |")
    if "country_or_region" in df:
        for region, region_df in df.groupby("country_or_region", sort=True):
            lines.extend(["", f"## {region}", ""])
            for _, row in region_df.head(5).iterrows():
                lines.append(f"- **{row.get('title', '')}** - {row.get('signal_type', 'Signal')} ({float(row.get('final_signal_score', 0)):.2f})")
    lines.extend(["", "---", "Demo or permitted feed metadata only. Not financial or political advice; verify original sources."])
    return "\n".join(lines)


def export_signals_to_markdown(df: pd.DataFrame, output_dir: str, top_n: int = 10) -> str:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / f"news_signal_report_{_timestamp()}.md"
    path.write_text(markdown_report(df, top_n), encoding="utf-8")
    return str(path)


def export_fetch_status_to_markdown(status_df: pd.DataFrame, health_df: pd.DataFrame, output_dir: str) -> str:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / f"live_fetch_status_{_timestamp()}.md"
    generated = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    scope = status_df.attrs.get("live_source_scope", "Configured live source scope")
    health_counts = health_df.get("health_status", pd.Series(dtype=str)).value_counts().to_dict()
    lines = ["# NewsSignalAgent Live Fetch Status", "", f"Generated: {generated}", f"Live source scope: {scope}", "",
             "## Health Summary", "", f"- Healthy: {health_counts.get('healthy', 0)}",
             f"- Warning: {health_counts.get('warning', 0)}", f"- Failed: {health_counts.get('failed', 0)}", ""]
    statuses = health_df.get("health_status", pd.Series(index=health_df.index, dtype=str))
    issues = health_df[statuses.isin(["warning", "failed"])]
    lines.extend(["## Warning / Failed Sources", ""])
    lines.extend([f"- {row.get('source', '')}: {row.get('health_status', '')} - {row.get('message', '')}" for _, row in issues.iterrows()] or ["- None"])
    lines.extend(["", "## Items Fetched", "", "| Source | Status | Items | Cache used |", "|---|---|---:|---|"])
    for _, row in status_df.iterrows():
        lines.append(f"| {row.get('source', '')} | {row.get('status', '')} | {int(row.get('items_fetched', 0))} | {bool(row.get('used_cache', False))} |")
    lines.extend(["", "## Compliance Note", "", "Only permitted feed/API metadata is processed. No paywall bypass, full article-body capture, credentials, or private content is included."])
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


def export_narrative_gap_report(gap_df: pd.DataFrame, output_dir: str, top_n: int = 10) -> str:
    from modules.narrative_gap_detector import generate_gap_explanation
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / f"narrative_gap_report_{_timestamp()}.md"
    generated = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    lines = ["# NewsSignalAgent Narrative Gap Report", "", f"Generated: {generated}", "",
             "Methodology: rule-based topic normalization and neutral source-group framing comparison.", "",
             "## Top Narrative Gaps", "", "| Score | Topic | Regions | Gap type |", "|---:|---|---|---|"]
    for _, row in gap_df.head(top_n).iterrows():
        lines.append(f"| {float(row.get('narrative_gap_score', 0)):.2f} | {row.get('normalized_topic', '')} | {row.get('regions_present', '')} | {row.get('dominant_gap_type', '')} |")
    lines.extend(["", "## Region Comparison and Opportunity Notes", ""])
    for _, row in gap_df.head(top_n).iterrows():
        lines.extend([f"### {row.get('normalized_topic', '')}", generate_gap_explanation(row),
                      f"- Business opportunity: {row.get('business_signal', '')}", f"- Risk: {row.get('risk_signal', '')}",
                      f"- Content angle: {row.get('content_angle', '')}", ""])
    lines.extend(["---", "Neutral framing comparison only. No truth or political-merit judgment. Not financial or political advice; verify original sources."])
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)
