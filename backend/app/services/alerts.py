alerts_store = []

def get_alerts():
    return alerts_store

def create_alert(alert: dict):
    alerts_store.append(alert)
    return {"status": "Alert added", "alert": alert}
