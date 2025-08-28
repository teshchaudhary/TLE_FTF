from fastapi import APIRouter, Query
from elasticsearch import Elasticsearch

router = APIRouter()
es = Elasticsearch("http://localhost:9200")
ALERTS_INDEX = "alerts"

@router.get("/alerts/search")
def search_alerts(
    severity: str = Query("All", description="Severity filter"),
    limit: int = Query(50, description="Max results")
):
    must_clauses = []

    if severity != "All":
        must_clauses.append({"match": {"severity": severity}})

    query = {"query": {"bool": {"must": must_clauses}}} if must_clauses else {"query": {"match_all": {}}}
    res = es.search(index=ALERTS_INDEX, body=query, size=limit)
    alerts = [hit["_source"] for hit in res["hits"]["hits"]]
    return alerts
