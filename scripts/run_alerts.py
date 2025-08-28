import time
import uuid
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch

ES_HOST = "http://localhost:9200"
INDEX_NAME = "alerts"

es = Elasticsearch(ES_HOST)

def generate_sample_alerts(count=2):
    """Generate `count` random alerts for testing."""
    sample_types = ["earthquake", "flood", "cyclone", "wildfire", "tsunami"]
    sample_severities = ["low", "medium", "high"]
    sample_locations = [
        {"lat": 28.61, "lon": 77.23},   # Delhi
        {"lat": 19.07, "lon": 72.87},   # Mumbai
        {"lat": 13.08, "lon": 80.27},   # Chennai
        {"lat": 22.57, "lon": 88.36},   # Kolkata
        {"lat": 26.85, "lon": 80.95},   # Lucknow
    ]

    alerts = []
    for _ in range(count):
        alert = {
            "id": str(uuid.uuid4()),
            "type": sample_types[_ % len(sample_types)],
            "severity": sample_severities[_ % len(sample_severities)],
            "description": f"Test alert {_ + 1} generated",
            "location": sample_locations[_ % len(sample_locations)],
            "created_at": datetime.utcnow().isoformat()
        }
        alerts.append(alert)
    return alerts

def insert_alert(alert):
    """Insert alert into Elasticsearch."""
    es.index(index=INDEX_NAME, id=alert["id"], document=alert)
    print(f"Inserted alert: {alert['id']}")

def cleanup_old_alerts(max_count=50):
    """Keep only the latest `max_count` alerts."""
    res = es.search(
        index=INDEX_NAME,
        body={"query": {"match_all": {}}, "sort": [{"created_at": {"order": "desc"}}]},
        size=1000
    )
    hits = res["hits"]["hits"]
    if len(hits) > max_count:
        for hit in hits[max_count:]:
            es.delete(index=INDEX_NAME, id=hit["_id"])
            print(f"Deleted old alert: {hit['_id']}")

# ----------------------
# Main loop
# ----------------------
if __name__ == "__main__":
    print("Starting alerts generator (testing mode: 2 alerts every 5 seconds)...")
    while True:
        alerts = generate_sample_alerts(count=2)
        for alert in alerts:
            insert_alert(alert)
        cleanup_old_alerts(max_count=50)
        print("Sleeping for 5 seconds before next batch...")
        time.sleep(5)
