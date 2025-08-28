from fastapi import FastAPI, Query
from elasticsearch import Elasticsearch
from .routes import disasters, alerts  # import alerts router


app = FastAPI()
app.include_router(disasters.router)
app.include_router(alerts.router)  
es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "disasters"

@app.get("/disasters/search")
def search_disasters(
    q: str = Query("", description="Search keyword"),
    disaster_type: str = Query("", description="Disaster type"),
    location: str = Query("", description="Location"),
    limit: int = Query(50, description="Max results")
):
    must_clauses = []

    if q:
        must_clauses.append({"multi_match": {"query": q, "fields": ["title", "description"]}})
    if disaster_type:
        must_clauses.append({"match": {"disaster_type": disaster_type}})
    if location:
        must_clauses.append({"match": {"location": location}})

    query = {"query": {"bool": {"must": must_clauses}}} if must_clauses else {"query": {"match_all": {}}}

    res = es.search(index=INDEX_NAME, body=query, size=limit)

    alerts = [hit["_source"] for hit in res["hits"]["hits"]]

    return alerts