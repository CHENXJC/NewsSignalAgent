import pandas as pd
from pathlib import Path
from modules.narrative_gap_detector import (FRAMES, GAP_COLUMNS, MATRIX_COLUMNS, assign_narrative_frame,
    build_topic_region_matrix, detect_narrative_gaps, generate_gap_report, normalize_topic_label)
from modules.export_utils import export_narrative_gap_report


def _sample():
    return pd.DataFrame([
        {"title": "Government policy supports AI adoption", "summary": "Official automation guidance", "topic": "AI automation", "tags": "policy;AI", "source": "x", "source_group": "china_policy", "country_or_region": "China", "final_signal_score": 88},
        {"title": "Companies invest in AI software", "summary": "Market investment expands", "topic": "AI automation", "tags": "market", "source": "y", "source_group": "us_business_tech", "country_or_region": "United States", "final_signal_score": 82},
        {"title": "Local retailers test automation", "summary": "Small business opportunity", "topic": "Small business automation", "tags": "local", "source": "z", "source_group": "australia_business", "country_or_region": "Australia", "final_signal_score": 79},
    ])


def test_normalize_ai_topic():
    assert normalize_topic_label("AI automation tools") == "AI & Automation"


def test_assign_frame_is_valid():
    assert assign_narrative_frame(_sample().iloc[0]) in FRAMES


def test_matrix_has_required_columns():
    matrix = build_topic_region_matrix(_sample())
    assert isinstance(matrix, pd.DataFrame)
    assert set(MATRIX_COLUMNS).issubset(matrix.columns)


def test_gaps_have_required_columns_and_bounded_score():
    gaps = detect_narrative_gaps(_sample())
    assert isinstance(gaps, pd.DataFrame)
    assert set(GAP_COLUMNS).issubset(gaps.columns)
    assert not gaps.empty
    assert gaps["narrative_gap_score"].between(0, 100).all()


def test_gap_report_is_markdown():
    report = generate_gap_report(_sample())
    assert report.startswith("# NewsSignalAgent Narrative Gap Report")
    assert "## Top Narrative Gaps" in report


def test_gap_report_export(tmp_path):
    path = export_narrative_gap_report(detect_narrative_gaps(_sample()), str(tmp_path))
    assert path.endswith(".md")
    assert "Narrative Gap Report" in Path(path).read_text(encoding="utf-8")
