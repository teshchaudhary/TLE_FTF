from elasticsearch import Elasticsearch
import json

es = Elasticsearch("http://localhost:9200")

# Load mapping
with open("elastic/mappings/alerts.json") as f:
    alerts_mapping = json.load(f)

# Create index if it doesn't exist
if not es.indices.exists(index="alerts"):
    es.indices.create(index="alerts", body=alerts_mapping)
    print("Alerts index created.")
else:
    print("Alerts index already exists.")
