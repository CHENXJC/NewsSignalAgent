"""NewsSignalAgent NEWS-006 public showcase dashboard."""
from pathlib import Path
import pandas as pd
import streamlit as st
import yaml

from modules.classifier import assign_region_bucket, classify_signal_type
from modules.data_loader import load_news_data
from modules.export_utils import export_fetch_status_to_markdown, export_narrative_gap_report, markdown_report
from modules.insight_generator import generate_action_suggestion, generate_basic_insight
from modules.news_cleaner import clean_news_dataframe
from modules.signal_scorer import score_news_dataframe
from modules.source_manager import list_available_sources, load_source_groups
from modules.source_health_checker import check_pilot_sources
from modules.narrative_gap_detector import (assign_narrative_frame, build_topic_region_matrix,
    detect_narrative_gaps, generate_gap_explanation, generate_gap_report, normalize_topic_label)

ROOT = Path(__file__).parent
MODE_MAP = {"Demo Data": "demo", "Live Sources": "live", "Hybrid Demo + Live": "hybrid"}
st.set_page_config(page_title="NewsSignalAgent", page_icon="📡", layout="wide")
st.markdown("""<style>
.hero {padding:2rem 2.2rem;border-radius:22px;background:linear-gradient(125deg,#edf6ff 0%,#f6f2ff 55%,#fff 100%);border:1px solid #e3eaf5;box-shadow:0 12px 36px rgba(39,67,115,.08);margin-bottom:1rem}
.hero .eyebrow {font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;color:#506d9c;font-weight:700;margin-bottom:.55rem}
.hero h1 {margin:0;color:#14213d;font-size:2.5rem}.hero p {color:#526078;margin:.55rem 0 0;font-size:1.08rem;max-width:850px}
.feature-grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.75rem;margin:1rem 0 1.25rem}
.feature-card {background:#fff;border:1px solid #e7ebf2;border-radius:15px;padding:1rem;box-shadow:0 5px 18px rgba(31,55,93,.05)}
.feature-card strong {display:block;color:#24395d;margin-bottom:.25rem}.feature-card span {color:#68758a;font-size:.88rem}
.stMetric {background:#fbfcfe;padding:14px;border-radius:15px;border:1px solid #e6ebf3;box-shadow:0 4px 14px rgba(31,55,93,.04)}
@media (max-width:900px){.feature-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>""", unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="eyebrow">Local-first AI portfolio workflow</div><h1>NewsSignalAgent</h1><p>Turn noisy news into business, market, policy, and cross-country narrative signals.</p></div>', unsafe_allow_html=True)
st.markdown("""<div class="feature-grid">
<div class="feature-card"><strong>Live RSS Pilot</strong><span>Six bounded public feeds with health and cache status.</span></div>
<div class="feature-card"><strong>Signal Score</strong><span>Transparent seven-part prioritization for every item.</span></div>
<div class="feature-card"><strong>Narrative Gap Detector</strong><span>Neutral framing differences across regional source groups.</span></div>
<div class="feature-card"><strong>Cross-country Comparison</strong><span>Coverage, dominant frames, keywords, and signal strength.</span></div>
<div class="feature-card"><strong>Exportable Reports</strong><span>CSV and Markdown outputs for review and presentation.</span></div>
<div class="feature-card"><strong>Compliance-first Design</strong><span>No paywall bypass, full article capture, or embedded secrets.</span></div>
</div>""", unsafe_allow_html=True)

st.sidebar.header("Data controls")
mode_label = st.sidebar.selectbox("Data Mode", list(MODE_MAP), index=0)
scope_label = st.sidebar.selectbox("Live Source Scope", ["NEWS-004 Pilot Sources Only", "All Enabled Sources"], index=0)
limit_per_source = st.sidebar.number_input("Limit per source", min_value=1, max_value=50, value=10)
use_cache = st.sidebar.checkbox("Use cache", value=True)
max_cache_age = st.sidebar.number_input("Max cache age minutes", min_value=0, max_value=1440, value=60)
refresh_live = st.sidebar.button("Refresh live sources", disabled=MODE_MAP[mode_label] == "demo")

try:
    source_config = load_source_groups(str(ROOT / "config" / "source_groups.yaml"))
    with (ROOT / "config" / "pilot_sources.yaml").open(encoding="utf-8") as handle:
        pilot_config = yaml.safe_load(handle)
    with (ROOT / "config" / "scoring_config.yaml").open(encoding="utf-8") as handle:
        scoring_config = yaml.safe_load(handle)
    news, fetch_status = load_news_data(MODE_MAP[mode_label], str(ROOT / "data" / "demo_news.csv"),
        str(ROOT / "config" / "source_groups.yaml"), int(limit_per_source), use_cache and not refresh_live,
        int(max_cache_age), pilot_config if scope_label == "NEWS-004 Pilot Sources Only" else None)
    scored = score_news_dataframe(clean_news_dataframe(news), scoring_config, source_config)
    if not scored.empty:
        scored["signal_type"] = scored.apply(classify_signal_type, axis=1)
        scored["region_bucket"] = scored.apply(assign_region_bucket, axis=1)
        scored["insight"] = scored.apply(generate_basic_insight, axis=1)
        scored["suggested_action"] = scored.apply(generate_action_suggestion, axis=1)
        scored["normalized_topic"] = scored.apply(lambda row: normalize_topic_label(" ".join(str(row.get(key, "")) for key in ("title", "summary", "topic", "tags"))), axis=1)
        scored["narrative_frame"] = scored.apply(assign_narrative_frame, axis=1)
except Exception as exc:
    st.error(f"Unable to load the local data pipeline: {exc}")
    st.stop()

if MODE_MAP[mode_label] in {"live", "hybrid"} and (fetch_status is not None) and not fetch_status.empty:
    live_count = int(fetch_status["items_fetched"].sum())
    if live_count == 0:
        st.warning("No live items were returned. The app remains stable; configure a verified official URL or switch to Demo Data.")

if MODE_MAP[mode_label] == "demo":
    st.info("Demo Data is the stable offline baseline: 26 original sample records and no network dependency.")
elif MODE_MAP[mode_label] == "live":
    st.warning("Live Sources shows current pilot metadata. Availability may change; use Demo Data if a feed is unavailable.")
else:
    st.info("Hybrid Demo + Live is recommended for the portfolio showcase: stable regional demo coverage plus current pilot metadata.")

st.sidebar.header("Signal filters")
group_options = sorted(scored["source_group"].dropna().unique()) if "source_group" in scored else []
region_options = sorted(scored["country_or_region"].dropna().unique()) if "country_or_region" in scored else []
topic_options = sorted(scored["topic"].dropna().unique()) if "topic" in scored else []
groups = st.sidebar.multiselect("Source group", group_options, default=group_options)
regions = st.sidebar.multiselect("Country / region", region_options, default=region_options)
topics = st.sidebar.multiselect("Topic", topic_options, default=topic_options)
minimum = st.sidebar.slider("Minimum signal score", 0, 100, 50)
if scored.empty:
    filtered = scored.copy()
else:
    filtered = scored[scored.source_group.isin(groups) & scored.country_or_region.isin(regions) & scored.topic.isin(topics) & (scored.final_signal_score >= minimum)]
st.sidebar.caption(f"NEWS-006 · {mode_label}")

tabs = st.tabs(["Global Signal Overview", "China Policy Signal", "Australia Local Signal", "US Market & Tech Signal",
                "Cross-country Comparison", "Narrative Gap Detector", "Fetch Status", "Raw Data", "Source Architecture"])


def signal_view(frame: pd.DataFrame, heading: str):
    st.subheader(heading)
    cols = st.columns(4)
    cols[0].metric("Signals", len(frame))
    cols[1].metric("Average score", f"{frame.final_signal_score.mean():.1f}" if len(frame) else "—")
    cols[2].metric("Top score", f"{frame.final_signal_score.max():.1f}" if len(frame) else "—")
    cols[3].metric("Topics", frame.topic.nunique() if "topic" in frame else 0)
    if frame.empty:
        st.info("No signals match these filters. Lower the minimum score or broaden the selected regions and topics.")
        return
    display = ["final_signal_score", "country_or_region", "topic", "signal_type", "title", "source"]
    st.dataframe(frame[display].head(10), use_container_width=True, hide_index=True)
    for _, row in frame.head(10).iterrows():
        with st.expander(f"{row.final_signal_score:.1f} · {row.title}"):
            st.write(row.insight)
            st.markdown(f"**Suggested action:** {row.suggested_action}")
            st.caption(f"Source attribution: {row.source} · {row.published_at} · {row.url}")


with tabs[0]:
    st.caption("Portfolio overview of the highest-priority policy, market, business, technology, and consumer signals.")
    signal_view(filtered, "Global signal overview")
    st.download_button("Download filtered CSV", filtered.to_csv(index=False).encode("utf-8-sig"), "news_signals.csv", "text/csv")
    st.download_button("Download Markdown report", markdown_report(filtered), "news_signal_report.md", "text/markdown")
with tabs[1]:
    st.caption("Demo-backed China policy narrative signals; no live China page scraping is performed.")
    signal_view(filtered[filtered.source_group == "china_policy"] if "source_group" in filtered else filtered, "China policy signals")
with tabs[2]:
    st.caption("Australian household, policy, employment, small-business, and market context.")
    signal_view(filtered[filtered.country_or_region == "Australia"] if "country_or_region" in filtered else filtered, "Australia local signals")
with tabs[3]:
    st.caption("US public, market, startup, and technology signals from demo or pilot metadata.")
    signal_view(filtered[filtered.country_or_region == "United States"] if "country_or_region" in filtered else filtered, "US market & technology signals")
with tabs[4]:
    st.subheader("Cross-country comparison")
    st.caption("See how normalized topics, source-group emphasis, and signal strength vary across four region buckets.")
    if filtered.empty:
        st.info("No data is available for comparison.")
    else:
        comparison = filtered.groupby("country_or_region").agg(signals=("id", "count"), average_score=("final_signal_score", "mean"), topics=("topic", "nunique")).round(2)
        st.dataframe(comparison, use_container_width=True)
        st.bar_chart(pd.crosstab(filtered.topic, filtered.country_or_region))
        st.subheader("Topic-region framing matrix")
        st.caption("Compare topic coverage, source-group emphasis, dominant frames, and average signal score without judging source correctness.")
        st.dataframe(build_topic_region_matrix(filtered), use_container_width=True, hide_index=True)
with tabs[5]:
    st.subheader("Narrative Gap Detector")
    st.info("Neutral framing comparison: this view highlights cross-region emphasis and omissions. It does not decide which source is right or wrong.")
    gap_df = detect_narrative_gaps(filtered)
    if gap_df.empty:
        st.info("At least two region buckets must cover the same normalized topic before a narrative gap can be compared.")
    else:
        metric_cols = st.columns(3)
        metric_cols[0].metric("Comparable topics", len(gap_df))
        metric_cols[1].metric("Top narrative gap score", f"{gap_df.narrative_gap_score.max():.1f}")
        region_coverage = max(len(str(value).split(", ")) for value in gap_df.regions_present)
        metric_cols[2].metric("Maximum region coverage", f"{region_coverage} / 4")
        st.dataframe(gap_df[["narrative_gap_score", "normalized_topic", "regions_present", "dominant_gap_type",
                            "business_signal", "risk_signal"]].head(10), use_container_width=True, hide_index=True)
        st.subheader("Dominant gap types")
        st.bar_chart(gap_df["dominant_gap_type"].value_counts())
        for _, gap in gap_df.head(10).iterrows():
            with st.expander(f"{gap.narrative_gap_score:.1f} · {gap.normalized_topic} · {gap.dominant_gap_type}"):
                st.write(generate_gap_explanation(gap))
                st.markdown(f"**Business signal:** {gap.business_signal}")
                st.markdown(f"**Risk signal:** {gap.risk_signal}")
                st.markdown(f"**Content angle:** {gap.content_angle}")
                st.markdown(f"**Suggested action:** {gap.suggested_action}")
                st.caption(f"Representative titles by region: {gap.representative_titles}")
        report_text = generate_gap_report(filtered)
        st.download_button("Download Narrative Gap Report", report_text, "narrative_gap_report.md", "text/markdown")
        if st.button("Export Narrative Gap Report"):
            report_path = export_narrative_gap_report(gap_df, str(ROOT / "outputs" / "reports"))
            st.success(f"Report created: {report_path}")
with tabs[6]:
    st.subheader("Fetch status")
    st.warning("Live source availability may change. Demo mode remains the stable portfolio baseline.")
    if fetch_status is None:
        st.info("Demo Data mode does not contact live sources.")
    else:
        fetch_status.attrs["live_source_scope"] = scope_label
        health_df = st.session_state.get("pilot_health", pd.DataFrame())
        health_counts = health_df.get("health_status", pd.Series(dtype=str)).value_counts()
        metrics = st.columns(5)
        metrics[0].metric("Healthy sources", int(health_counts.get("healthy", 0)))
        metrics[1].metric("Warning sources", int(health_counts.get("warning", 0)))
        metrics[2].metric("Failed sources", int(health_counts.get("failed", 0)))
        metrics[3].metric("Items fetched", int(fetch_status["items_fetched"].sum()))
        metrics[4].metric("Cache used", int(fetch_status["used_cache"].sum()))
        st.dataframe(fetch_status, use_container_width=True, hide_index=True)
        st.subheader("Pilot Source Health")
        if st.button("Run source health check"):
            with st.spinner("Checking the small pilot source set..."):
                st.session_state["pilot_health"] = check_pilot_sources(source_config, pilot_config)
            st.rerun()
        health_df = st.session_state.get("pilot_health", pd.DataFrame())
        if health_df.empty:
            st.info("Run the bounded health check to verify current pilot availability.")
        else:
            st.dataframe(health_df, use_container_width=True, hide_index=True)
            if st.button("Generate live fetch status report"):
                report_path = export_fetch_status_to_markdown(fetch_status, health_df, str(ROOT / "outputs" / "reports"))
                st.success(f"Report created: {report_path}")
with tabs[7]:
    st.subheader("Processed data")
    st.caption("Normalized demo or permitted feed metadata with scoring, attribution, topic, and narrative-frame fields.")
    st.dataframe(scored, use_container_width=True, hide_index=True)
with tabs[8]:
    st.subheader("Source architecture")
    st.caption("Review analytical roles, access modes, verification status, and capture policies. Add only verified official RSS/API URLs.")
    st.dataframe(list_available_sources(source_config), use_container_width=True, hide_index=True)

st.caption("Portfolio/demo workflow. Live mode fetches feed/API metadata only. Not financial advice, political advice, or a replacement for original sources.")
