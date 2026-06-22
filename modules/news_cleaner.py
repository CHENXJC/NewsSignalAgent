"""Simple, transparent news cleaning utilities."""
import pandas as pd


def deduplicate_news(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    if "title" not in result:
        result["title"] = ""
    result["normalized_title"] = result["title"].fillna("").astype(str).str.lower().str.strip().str.replace(r"\s+", " ", regex=True)
    if "url" in result:
        normalized_url = result["url"].fillna("").astype(str).str.strip().str.lower()
        with_url = result[normalized_url.ne("")].drop_duplicates(subset="url", keep="first")
        without_url = result[normalized_url.eq("")]
        result = pd.concat([with_url, without_url]).sort_index()
    return result.drop_duplicates(subset="normalized_title", keep="first").reset_index(drop=True)


def clean_news_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for column in ["title", "summary", "topic", "tags", "published_at", "url"]:
        if column not in result:
            result[column] = ""
        result[column] = result[column].fillna("").astype(str).str.strip()
    return deduplicate_news(result)
