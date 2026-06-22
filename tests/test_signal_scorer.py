from pathlib import Path
import yaml
from modules.data_loader import load_demo_news
from modules.signal_scorer import score_news_dataframe
from modules.source_manager import load_source_groups

ROOT = Path(__file__).parents[1]


def _scored():
    df = load_demo_news(str(ROOT / "data" / "demo_news.csv"))
    sources = load_source_groups(str(ROOT / "config" / "source_groups.yaml"))
    with (ROOT / "config" / "scoring_config.yaml").open(encoding="utf-8") as handle:
        scoring = yaml.safe_load(handle)
    return score_news_dataframe(df, scoring, sources)


def test_final_signal_score_added_and_bounded():
    scored = _scored()
    assert "final_signal_score" in scored.columns
    assert scored.final_signal_score.between(0, 100).all()


def test_policy_anchor_has_meaningful_policy_score():
    anchor = _scored().query("source == 'cctv_xinwen_lianbo'").iloc[0]
    assert anchor.policy_narrative_score >= 90
