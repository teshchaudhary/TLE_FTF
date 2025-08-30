import os
import re
import time
import logging
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import praw
from elasticsearch import Elasticsearch, helpers
from transformers import pipeline
from geopy.geocoders import Nominatim

# -----------------------
# Config & Logging
# -----------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

ES_HOST = os.getenv("ES_HOST")
ES_INDEX = os.getenv("ES_INDEX")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

BATCH_SIZE = 16
CLASSIFY_THRESHOLD = 0.25
SECONDARY_THRESHOLD = 0.15

DISASTER_TYPES = ["earthquake","flood","cyclone","wildfire","landslide","volcano","drought","tsunami"]
SYNONYMS = {
    "quake":"earthquake","tremor":"earthquake","aftershock":"earthquake","seismic":"earthquake","shock":"earthquake",
    "flash flood":"flood","deluge":"flood","inundation":"flood","overflow":"flood","swamped":"flood","flooding":"flood",
    "hurricane":"cyclone","typhoon":"cyclone","storm":"cyclone","superstorm":"cyclone","gale":"cyclone","monsoon":"cyclone",
    "bushfire":"wildfire","forest fire":"wildfire","wild fire":"wildfire","firestorm":"wildfire","blaze":"wildfire",
    "mudslide":"landslide","rockslide":"landslide","debris flow":"landslide","avalanche":"landslide","landslip":"landslide",
    "eruption":"volcano","lava":"volcano","pyroclastic":"volcano","magma":"volcano","ash cloud":"volcano","volcanic":"volcano",
    "dry spell":"drought","water scarcity":"drought","famine":"drought","arid":"drought","desertification":"drought","heatwave":"drought",
    "tidal wave":"tsunami","seismic sea wave":"tsunami","giant wave":"tsunami","ocean surge":"tsunami","tsunami waves":"tsunami"
}

# -----------------------
# Initialize clients
# -----------------------
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent="reddit_to_es/0.1"
)

es = Elasticsearch([ES_HOST])
if not es.ping():
    raise ConnectionError(f"Cannot connect to Elasticsearch at {ES_HOST}")

classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli", device=-1)
ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple", device=-1)
sentiment = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", device=-1)
geolocator = Nominatim(user_agent="disaster_monitor", timeout=10, scheme="https")

# -----------------------
# Helper Functions
# -----------------------
def normalize_text(t: str) -> str:
    if not t: return ""
    s = t.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def synonym_keyword_fallback(text: str) -> List[str]:
    text_l = normalize_text(text)
    matches = set()
    for syn in sorted(SYNONYMS.keys(), key=lambda x: -len(x)):
        if re.search(rf"\b{re.escape(syn)}\b", text_l):
            matches.add(SYNONYMS[syn])
    for d in DISASTER_TYPES:
        if re.search(rf"\b{re.escape(d)}\b", text_l):
            matches.add(d)
    return list(matches)[:2]

def extract_location(title: str, description: str) -> str:
    text = " ".join(filter(None,[title,description]))
    if not text: return "India"
    ents = ner(text)
    locs = [e.get("word") for e in ents if e.get("entity_group") in ("LOC","GPE")]
    return locs[0] if locs else "India"

def get_geo(location: str) -> dict:
    default_geo = {"lat": 20.5937, "lon": 78.9629}
    if not location: return default_geo
    for _ in range(3):
        try:
            loc = geolocator.geocode(location)
            if loc: return {"lat": loc.latitude, "lon": loc.longitude}
        except: time.sleep(1)
    return default_geo

def compute_severity(text: str) -> str:
    if not text: return "low"
    out = sentiment(text[:512])[0]
    label, score = out["label"], float(out["score"])
    if label=="NEGATIVE" and score>0.7: return "high"
    if label=="NEGATIVE": return "medium"
    return "low"

# -----------------------
# Fetch + Enrich Reddit
# -----------------------
def fetch_reddit_posts(subreddit_name: str, limit: int=100, query: str="disaster"):
    """
    Fetch latest posts matching the query.
    """
    posts = []
    for post in reddit.subreddit(subreddit_name).search(query=query, sort="new", limit=limit):
        posts.append({
            "title": post.title,
            "description": post.selftext[:200],
            "content": post.selftext,
            "url": post.url,
            "source": post.subreddit.display_name,
            "publishedAt": datetime.utcfromtimestamp(post.created_utc)
        })
    return posts

def enrich_reddit_posts(raw_posts: List[Dict]) -> pd.DataFrame:
    records = []
    for p in raw_posts:
        loc = extract_location(p["title"], p["content"])
        rec = {
            "title": p["title"],
            "description": p["description"],
            "content": p["content"],
            "url": p["url"],
            "source": "reddit",
            "publishedAt": p["publishedAt"],
            "disaster_type": synonym_keyword_fallback(p["title"]+" "+p["content"]),
            "location": loc,
            "severity": compute_severity(p["title"]+" "+p["content"]),
            "geo": get_geo(loc)
        }
        records.append(rec)
    return pd.DataFrame(records)

# -----------------------
# Elasticsearch Indexing
# -----------------------
def index_into_es(df: pd.DataFrame, es_client: Elasticsearch, index_name: str):
    actions = [
        {
            "_op_type":"index",
            "_index":index_name,
            "_id":r["url"],
            "_source":r.to_dict() if isinstance(r,pd.Series) else r
        }
        for _,r in df.iterrows()
    ]
    if actions:
        helpers.bulk(es_client, actions)
        logging.info("Indexed %d documents into '%s'.", len(actions), index_name)

# -----------------------
# Main Runner
# -----------------------
def main(limit: int=100, query: str="disaster"):
    """
    :param limit: number of latest posts to fetch
    :param query: search query string
    """
    logging.info("Fetching Reddit posts...")
    raw_posts = fetch_reddit_posts("naturaldisasters", limit=limit, query=query)
    if not raw_posts:
        logging.info("No Reddit posts found.")
        return

    df = enrich_reddit_posts(raw_posts)
    index_into_es(df, es, ES_INDEX)

if __name__ == "__main__":
    main()
