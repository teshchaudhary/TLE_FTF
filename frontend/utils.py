import requests

def fetch_disasters(api_url, filters):
    params = {"q": filters["q"], "limit": filters["limit"]}
    if filters["disaster_type"] != "All":
        params["disaster_type"] = filters["disaster_type"]
    if filters["date_range"]:
        params["start_date"] = filters["date_range"][0].isoformat()
        params["end_date"] = filters["date_range"][1].isoformat()
    if filters["location"].strip():
        params["location"] = filters["location"]

    try:
        res = requests.get(f"{api_url}/disasters/search", params=params)
        res.raise_for_status()
        return res.json()
    except:
        return []

def fetch_alerts(api_url, filters):
    params = {"severity": filters["alert_severity"], "limit": filters["limit"]}
    try:
        res = requests.get(f"{api_url}/alerts/search", params=params)
        res.raise_for_status()
        return res.json()
    except:
        return []
