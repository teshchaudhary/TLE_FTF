# backend/app/services/nlp.py
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="disaster_monitor")

def geocode_location(location: str):
    """Convert location name to geo coordinates"""
    if not location:
        return None
    try:
        loc = geolocator.geocode(location)
        if loc:
            return {"lat": loc.latitude, "lon": loc.longitude}
    except Exception:
        return None
    return None

def detect_severity(text: str):
    """Naive severity detection using keyword rules"""
    if not text:
        return "low"
    text = text.lower()
    if any(word in text for word in ["massive", "severe", "deadly", "magnitude", "killed"]):
        return "high"
    elif any(word in text for word in ["damage", "affected", "evacuated"]):
        return "medium"
    else:
        return "low"
