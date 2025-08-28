# backend/app/services/fetch_news.py
from .nlp import geocode_location, detect_severity

def process_article(article: dict) -> dict:
    """Clean and enrich article with geo + severity"""
    location = article.get("location", "")
    geo = geocode_location(location)
    severity = detect_severity(
        (article.get("title") or "") + " " + (article.get("description") or "")
    )

    return {
        "title": article.get("title"),
        "disaster_type": article.get("disaster_type"),
        "location": location,
        "geo": geo,
        "severity": severity,
        "publishedAt": article.get("publishedAt"),
    }
