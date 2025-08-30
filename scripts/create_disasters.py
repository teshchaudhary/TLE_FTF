from elasticsearch import Elasticsearch
import json

es = Elasticsearch("http://localhost:9200")

# Load mapping
with open("elastic/mappings/disasters.json") as f:
    alerts_mapping = json.load(f)

# Create index if it doesn't exist
if not es.indices.exists(index="disasters"):
    es.indices.create(index="disasters", body=alerts_mapping)
    print("Disasters index created.")
else:
    print("Disasters index already exists.")
