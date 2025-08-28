from fastapi import APIRouter, Query
from backend.app.services.elastic import search_disasters

router = APIRouter()

@router.get("/")
def get_disasters(
    query: str = Query(None, description="Search keyword"),
    lat: float = Query(None, description="Latitude"),
    lon: float = Query(None, description="Longitude"),
    radius: str = Query("50km", description="Search radius, e.g., 50km")
):
    return search_disasters(query=query, lat=lat, lon=lon, radius=radius)
