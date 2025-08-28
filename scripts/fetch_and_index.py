import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import logging
import re
import time
from datetime import datetime
from typing import List, Dict, Optional

import requests
import pandas as pd
from dotenv import load_dotenv
from transformers import pipeline
from elasticsearch import Elasticsearch, helpers
from geopy.geocoders import Nominatim

# -----------------------
# Config & Logging
# -----------------------
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
if not NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY not found in environment/.env")

ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
ES_INDEX = os.getenv("ES_INDEX", "disasters")
PARQUET_PATH = os.getenv("PARQUET_PATH", "data/disasters.parquet")

CLASSIFY_THRESHOLD = float(os.getenv("CLASSIFY_THRESHOLD", 0.25))
SECONDARY_THRESHOLD = float(os.getenv("SECONDARY_THRESHOLD", 0.15))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 16))
PER_DISASTER_FETCH = int(os.getenv("PER_DISASTER_FETCH", 100))

# -----------------------
# Disaster Types & Synonyms
# -----------------------
DISASTER_TYPES = [
    "earthquake", "flood", "cyclone", "wildfire",
    "landslide", "volcano", "drought", "tsunami"
]

SYNONYMS = {
    "quake": "earthquake", "tremor": "earthquake", "aftershock": "earthquake",
    "seismic": "earthquake", "richter": "earthquake", "shock": "earthquake",
    "flash flood": "flood", "deluge": "flood", "inundation": "flood",
    "overflow": "flood", "swamped": "flood", "flooding": "flood", "torrent": "flood",
    "hurricane": "cyclone", "typhoon": "cyclone", "storm": "cyclone",
    "superstorm": "cyclone", "gale": "cyclone", "monsoon": "cyclone",
    "cyclonic": "cyclone", "tropical storm": "cyclone",
    "bushfire": "wildfire", "forest fire": "wildfire", "wild fire": "wildfire",
    "firestorm": "wildfire", "blaze": "wildfire", "grassfire": "wildfire",
    "mudslide": "landslide", "rockslide": "landslide", "debris flow": "landslide",
    "avalanche": "landslide", "landslip": "landslide", "earth slip": "landslide",
    "eruption": "volcano", "lava": "volcano", "pyroclastic": "volcano",
    "magma": "volcano", "ash cloud": "volcano", "volcanic": "volcano",
    "dry spell": "drought", "water scarcity": "drought", "famine": "drought",
    "arid": "drought", "desertification": "drought", "heatwave": "drought",
    "droughts": "drought", "parched": "drought",
    "tidal wave": "tsunami", "seismic sea wave": "tsunami", "giant wave": "tsunami",
    "ocean surge": "tsunami", "tsunami waves": "tsunami",
}

# -----------------------
# Initialize clients & pipelines
# -----------------------
es = Elasticsearch([ES_HOST])
if not es.ping():
    raise ConnectionError(f"Cannot connect to Elasticsearch at {ES_HOST}")

classifier = pipeline("zero-shot-classification",
                      model="typeform/distilbert-base-uncased-mnli", device=-1)

ner = pipeline("ner",
               model="dslim/bert-base-NER",
               aggregation_strategy="simple",
               device=-1)

sentiment = pipeline("sentiment-analysis",
                     model="distilbert-base-uncased-finetuned-sst-2-english",
                     device=-1)

geolocator = Nominatim(
    user_agent="disaster_monitor",
    timeout=10,
    scheme="https",
)

# -----------------------
# Helper functions
# -----------------------
def normalize_text(t: str) -> str:
    if not t:
        return ""
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
    return list(matches)[:2]  # top 2

def classify_batch_top2(texts: List[str], candidate_labels: List[str]) -> List[List[str]]:
    results = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i+BATCH_SIZE]
        outs = classifier(batch_texts, candidate_labels, multi_label=True, batch_size=BATCH_SIZE)
        if isinstance(outs, dict):
            outs = [outs]
        for out in outs:
            labels, scores = out["labels"], out["scores"]
            combined = []
            for lbl, sc in zip(labels, scores):
                if sc >= CLASSIFY_THRESHOLD:
                    combined.append(lbl)
                if len(combined) == 2:
                    break
            if len(combined) < 2:
                for lbl, sc in zip(labels, scores):
                    if sc >= SECONDARY_THRESHOLD and lbl not in combined:
                        combined.append(lbl)
                    if len(combined) == 2:
                        break
            results.append(combined if combined else ["unknown"])
    return results

def extract_location(title: str, description: str) -> str:
    text = " ".join(filter(None, [title, description]))
    if not text:
        return "India"
    ents = ner(text)
    locs = [e.get("word") for e in ents if e.get("entity_group") in ("LOC", "GPE")]
    return locs[0] if locs else "India"

def get_geo(location: str) -> dict:
    default_geo = {"lat": 20.5937, "lon": 78.9629}  # India default
    if not location:
        return default_geo
    for _ in range(3):
        try:
            loc = geolocator.geocode(location)
            if loc:
                return {"lat": loc.latitude, "lon": loc.longitude}
        except Exception as e:
            logging.warning("Geo lookup failed for %s: %s", location, e)
            time.sleep(1)
    return default_geo

def compute_severity(text: str) -> str:
    if not text:
        return "low"
    out = sentiment(text[:512])[0]
    label, score = out["label"], float(out["score"])
    if label == "NEGATIVE" and score > 0.7:
        return "high"
    if label == "NEGATIVE":
        return "medium"
    return "low"

def parse_published_at(s: Optional[str]) -> datetime:
    if not s:
        return datetime.utcnow()
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        try:
            return datetime.fromisoformat(s)
        except Exception:
            return datetime.utcnow()

# -----------------------
# Fetch + enrich
# -----------------------
def fetch_for_query(query: str, page_size: int = 100) -> List[Dict]:
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f"{query} AND India",
        "language": "en",
        "pageSize": page_size,
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json().get("articles", [])
    except Exception as e:
        logging.error("Failed fetch for %s: %s", query, e)
        return []

def enrich_articles(raw_articles: List[Dict]) -> pd.DataFrame:
    records, texts_to_classify, idxs = [], [], []
    for i, a in enumerate(raw_articles):
        title, desc, content = a.get("title", ""), a.get("description", ""), a.get("content", "")
        combined = " ".join([title, desc, content]).strip()
        rec = {
            "title": title, "description": desc, "content": content,
            "url": a.get("url"), "source": (a.get("source") or {}).get("name"),
            "publishedAt": parse_published_at(a.get("publishedAt"))
        }
        # synonym fallback first
        syns = synonym_keyword_fallback(combined)
        if syns:
            rec["disaster_type"] = syns
        else:
            rec["disaster_type"] = None
            texts_to_classify.append(combined or title or desc)
            idxs.append(i)
        records.append(rec)

    if texts_to_classify:
        preds = classify_batch_top2(texts_to_classify, DISASTER_TYPES)
        for k, idx in enumerate(idxs):
            records[idx]["disaster_type"] = preds[k]

    # fallback + location + severity + geo
    for rec in records:
        if not rec.get("disaster_type") or rec.get("disaster_type") == ["unknown"]:
            rec["disaster_type"] = synonym_keyword_fallback(
                " ".join([rec["title"], rec["description"], rec["content"]])
            ) or ["unknown"]
        rec["location"] = extract_location(rec["title"], rec["description"])
        rec["severity"] = compute_severity(" ".join([rec["title"], rec["description"], rec["content"]]))
        rec["geo"] = get_geo(rec["location"])

    df = pd.DataFrame(records)
    return df[["title","description","content","url","source","publishedAt","disaster_type","location","severity","geo"]]

# -----------------------
# Parquet merge & dedup
# -----------------------
def append_to_parquet(new_df: pd.DataFrame, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        try:
            existing = pd.read_parquet(path)
            combined = pd.concat([existing, new_df], ignore_index=True)
            combined.sort_values("publishedAt", ascending=False, inplace=True)
            combined = combined.drop_duplicates(subset=["url"], keep="first")
            combined.to_parquet(path, index=False)
            return combined, existing.shape[0], new_df.shape[0]
        except Exception as e:
            logging.error("Failed merging parquet: %s", e)
            new_df.to_parquet(path, index=False)
            return new_df, 0, new_df.shape[0]
    else:
        new_df.to_parquet(path, index=False)
        return new_df, 0, new_df.shape[0]

# -----------------------
# Elasticsearch indexing
# -----------------------
def index_into_es(df: pd.DataFrame, es_client: Elasticsearch, index_name: str):
    actions = []
    for _, r in df.iterrows():
        _id = r.get("url")
        source = r.to_dict()
        for k, v in source.items():
            if isinstance(v, list):
                source[k] = v
            elif pd.isna(v):
                source[k] = None
            elif isinstance(v, (pd.Timestamp, datetime)):
                source[k] = v.isoformat()
            elif isinstance(v, bool):
                source[k] = bool(v)
            elif isinstance(v, (int, float, str, dict)):
                source[k] = v
            else:
                source[k] = str(v)
        actions.append({
            "_op_type": "index",
            "_index": index_name,
            "_id": _id,
            "_source": source
        })
    success, _ = helpers.bulk(es_client, actions, stats_only=True, request_timeout=120)
    return success

# -----------------------
# Main run
# -----------------------
def main():
    all_new_records = []
    seen_urls = set()
    if os.path.exists(PARQUET_PATH):
        try:
            existing = pd.read_parquet(PARQUET_PATH)
            seen_urls = set(existing["url"].dropna().tolist())
            logging.info("Found existing parquet with %d records.", len(seen_urls))
        except Exception as e:
            logging.warning("Could not read existing parquet: %s", e)

    for disaster in DISASTER_TYPES:
        logging.info("Fetching up to %d articles for '%s'...", PER_DISASTER_FETCH, disaster)
        raw = fetch_for_query(disaster, page_size=PER_DISASTER_FETCH)
        new_raw = [a for a in raw if a.get("url") not in seen_urls]
        if not new_raw:
            logging.info("No new articles for %s", disaster)
            continue

        logging.info("Enriching %d articles...", len(new_raw))
        df_new = enrich_articles(new_raw)
        df_new = df_new.drop_duplicates(subset=["url"])
        all_new_records.append(df_new)
        seen_urls.update(df_new["url"].dropna().tolist())
        time.sleep(1.0)

    if not all_new_records:
        logging.info("No new articles to process. Exiting.")
        return

    new_df = pd.concat(all_new_records, ignore_index=True)
    logging.info("Total new enriched records: %d", new_df.shape[0])

    combined_df, existing_count, new_count = append_to_parquet(new_df, PARQUET_PATH)
    logging.info("Parquet updated: existing=%d, new_added=%d, total_after=%d",
                 existing_count, new_count, combined_df.shape[0])

    logging.info("Indexing %d new docs into Elasticsearch '%s'...", new_df.shape[0], ES_INDEX)
    n_indexed = index_into_es(new_df, es, ES_INDEX)
    logging.info("Indexed %d documents.", n_indexed)

if __name__ == "__main__":
    main()
