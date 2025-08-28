from elasticsearch import Elasticsearch
from datetime import datetime
import uuid
import os

# Elasticsearch setup
ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
es = Elasticsearch(hosts=[ES_HOST])

ALERT_INDEX = "alerts"

# Ensure index exists with proper mapping
def init_index():
    if not es.indices.exists(index=ALERT_INDEX):
        es.indices.create(
            index=ALERT_INDEX,
            body={
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "type": {"type": "keyword"},
                        "severity": {"type": "keyword"},
                        "description": {"type": "text"},
                        "location": {"type": "geo_point"},
                        "created_at": {"type": "date"}
                    }
                }
            }
        )

# Create an alert
def create_alert(alert_data: dict):
    init_index()  # make sure index exists

    alert = {
        "id": str(uuid.uuid4()),
        "type": alert_data.get("type"),
        "severity": alert_data.get("severity"),
        "description": alert_data.get("description", ""),
        "location": alert_data.get("location"),  # {"lat": xx, "lon": yy}
        "created_at": datetime.utcnow()
    }
    es.index(index=ALERT_INDEX, id=alert["id"], document=alert)
    return alert

# Get all alerts (with pagination)
def get_alerts(limit=100, offset=0):
    init_index()
    resp = es.search(
        index=ALERT_INDEX,
        body={"query": {"match_all": {}}},
        size=limit,
        from_=offset
    )
    return [hit["_source"] for hit in resp["hits"]["hits"]]

# Search alerts by text (optional feature)
def search_alerts(query: str):
    init_index()
    resp = es.search(
        index=ALERT_INDEX,
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["type", "description", "severity"]
                }
            }
        }
    )
    return [hit["_source"] for hit in resp["hits"]["hits"]]

# Dummy disaster search (to fix missing import issue)
def search_disasters(query: str):
    # You can later hook this to a "disasters" index
    return search_alerts(query)
