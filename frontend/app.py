import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
import altair as alt
from datetime import datetime

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="🌍 Disaster Monitor", layout="wide")
st.title("🌍 Disaster Monitor Dashboard")

# ----------------------
# Sidebar Filters
# ----------------------
st.sidebar.header("🔎 Search Filters")

# Keyword filter
q = st.sidebar.text_input("Keyword")

# Disaster type dropdown with "All"
disaster_type_options = ["All", "earthquake", "flood", "cyclone", "wildfire", "tsunami"]
selected_disaster_type = st.sidebar.selectbox("Disaster Type", disaster_type_options, index=0)

# Disaster severity dropdown with "All"
severity_options = ["All", "low", "medium", "high"]
selected_disaster_severity = st.sidebar.selectbox("Disaster Severity", severity_options, index=0)

# Location filter
location = st.sidebar.text_input("Location")

# Date filter
all_dates = st.sidebar.checkbox("All Dates", value=True)
if not all_dates:
    date_range = st.sidebar.date_input(
        "Published Date Range",
        value=[datetime(2023, 1, 1), datetime.today()]
    )
else:
    date_range = None

# Limit filter
limit = st.sidebar.slider("Max Results", 10, 200, 50)

# Alerts severity dropdown with "All"
selected_alert_severity = st.sidebar.selectbox("Alert Severity", severity_options, index=0)

# Trigger ingestion
if st.sidebar.button("⚡ Fetch Latest News"):
    try:
        requests.post(f"{API_URL}/disasters/fetch")
        st.sidebar.success("Ingestion started!")
    except Exception as e:
        st.sidebar.error(f"Failed to start ingestion: {e}")

# ----------------------
# Fetch Disasters
# ----------------------
params = {"q": q, "limit": limit}
if selected_disaster_type != "All":
    params["disaster_type"] = selected_disaster_type
if date_range:
    params["start_date"] = date_range[0].isoformat()
    params["end_date"] = date_range[1].isoformat()
if location.strip():
    params["location"] = location

with st.spinner("Fetching disasters..."):
    try:
        res = requests.get(f"{API_URL}/disasters/search", params=params)
        res.raise_for_status()
        disasters_data = res.json()
    except Exception as e:
        st.error(f"Error fetching disasters: {e}")
        disasters_data = []

# ----------------------
# Fetch Alerts
# ----------------------
alert_params = {"severity": selected_alert_severity, "limit": limit}
with st.spinner("Fetching alerts..."):
    try:
        res_alerts = requests.get(f"{API_URL}/alerts/search", params=alert_params)
        res_alerts.raise_for_status()
        alerts_data = res_alerts.json()
    except Exception as e:
        st.error(f"Error fetching alerts: {e}")
        alerts_data = []

# ----------------------
# Process Disasters DataFrame
# ----------------------
if disasters_data:
    df_disasters = pd.DataFrame(disasters_data)
    df_disasters["layer"] = "Disaster"

    if selected_disaster_severity != "All":
        df_disasters = df_disasters[df_disasters["severity"] == selected_disaster_severity]

    if "geo" in df_disasters.columns:
        df_disasters["lat"] = df_disasters["geo"].apply(lambda g: g.get("lat") if isinstance(g, dict) else None)
        df_disasters["lon"] = df_disasters["geo"].apply(lambda g: g.get("lon") if isinstance(g, dict) else None)

    severity_map = {"low": 1, "medium": 3, "high": 5}
    df_disasters["weight"] = df_disasters["severity"].map(severity_map).fillna(1)

    color_map = {"low": [0, 255, 0, 160], "medium": [255, 165, 0, 160], "high": [255, 0, 0, 160]}
    default_color = [200, 30, 0, 160]
    df_disasters["color"] = df_disasters["severity"].apply(lambda x: color_map.get(x, default_color))
else:
    df_disasters = pd.DataFrame()

# ----------------------
# Process Alerts DataFrame
# ----------------------
df_alerts = pd.DataFrame()  # always initialize
if alerts_data:
    df_alerts = pd.DataFrame(alerts_data)
    df_alerts["layer"] = "Alert"

    if not df_alerts.empty and "location" in df_alerts.columns:
        df_alerts["lat"] = df_alerts["location"].apply(lambda g: g.get("lat") if isinstance(g, dict) else None)
        df_alerts["lon"] = df_alerts["location"].apply(lambda g: g.get("lon") if isinstance(g, dict) else None)

    alert_color_map = {"low": [0, 0, 255, 160], "medium": [0, 128, 255, 160], "high": [0, 255, 255, 160]}
    default_alert_color = [0, 0, 255, 160]
    df_alerts["color"] = df_alerts["severity"].apply(lambda x: alert_color_map.get(x, default_alert_color))

# ----------------------
# Latest Alert Marquee
# ----------------------
if not df_alerts.empty:
    latest_alert = df_alerts.sort_values("created_at", ascending=False).iloc[0]
    marquee_html = f"""
    <marquee behavior="scroll" direction="left" scrollamount="6" style="
        background: linear-gradient(90deg, #ff0000, #ff6347);
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 10px;
        border-radius: 8px;">
        🚨 {latest_alert['type'].title()} Alert - {latest_alert['severity'].title()}: {latest_alert['description']}
    </marquee>
    """
    st.markdown(marquee_html, unsafe_allow_html=True)

st.markdown("---")

# ----------------------
# 1️⃣ Disaster Table
# ----------------------
st.subheader("📋 Disaster List")
st.dataframe(
    df_disasters[["title", "disaster_type", "severity", "location", "publishedAt", "source", "url"]] if not df_disasters.empty else pd.DataFrame(),
    width='stretch',
    height=400
)

st.markdown("---")

# ----------------------
# 2️⃣ Timeline
# ----------------------
st.subheader("📈 Disaster Timeline")
if not df_disasters.empty:
    df_disasters["publishedAt"] = pd.to_datetime(df_disasters["publishedAt"])
    timeline = df_disasters.groupby([df_disasters["publishedAt"].dt.date, "severity"]).size().reset_index(name="count")
    chart = alt.Chart(timeline).mark_bar().encode(
        x="publishedAt:T",
        y="count:Q",
        color="severity:N",
        tooltip=["publishedAt:T", "severity:N", "count:Q"],
    ).properties(width=900, height=300)
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No timeline data available.")

st.markdown("---")

# ----------------------
# 3️⃣ Alerts Table
# ----------------------
st.subheader("🚨 Alerts")
st.dataframe(
    df_alerts[["id", "type", "severity", "created_at"]] if not df_alerts.empty else pd.DataFrame(),
    width='stretch',
    height=200
)

st.markdown("---")

# ----------------------
# Map Legend
# ----------------------
st.markdown(
    """
    **Map Legend:**  
    <span style="color:#FF0000">■</span> Disaster (High)  
    <span style="color:#FFA500">■</span> Disaster (Medium)  
    <span style="color:#00FF00">■</span> Disaster (Low)  
    <span style="color:#0000FF">■</span> Alert
    """,
    unsafe_allow_html=True
)

# ----------------------
# 4️⃣ Disaster + Alerts Map
# ----------------------
st.subheader("🗺️ Disaster & Alerts Map")
map_layers = []

# Disasters Layer
if not df_disasters.empty and df_disasters["lat"].notnull().any():
    map_layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=df_disasters.dropna(subset=["lat", "lon"]),
            get_position="[lon, lat]",
            get_color="color",
            get_radius=30000,
            pickable=True
        )
    )
    map_layers.append(
        pdk.Layer(
            "HeatmapLayer",
            data=df_disasters.dropna(subset=["lat", "lon"]),
            get_position="[lon, lat]",
            get_weight="weight",
            radiusPixels=60,
            intensity=1,
            threshold=0.02,
        )
    )

# Alerts Layer
if not df_alerts.empty and df_alerts["lat"].notnull().any():
    map_layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=df_alerts.dropna(subset=["lat", "lon"]),
            get_position="[lon, lat]",
            get_color="color",
            get_radius=30000,
            pickable=True
        )
    )

# Deck Visualization
if map_layers:
    st.pydeck_chart(
        pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=20.5937,
                longitude=78.9629,
                zoom=4,
                pitch=30,
            ),
            layers=map_layers,
            tooltip={
                "html": "<b>Layer:</b> {layer}<br><b>Title:</b> {title}<br>Type: {disaster_type}<br>Severity: {severity}<br>Published: {publishedAt}<br>Source: {source}<br><a href='{url}' target='_blank'>Link</a>",
                "style": {"color": "white"},
            },
        )
    )
else:
    st.info("No geo-location data to display on map.")
