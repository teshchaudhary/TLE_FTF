import streamlit as st
import pydeck as pdk
import pandas as pd

def show_map(disasters_data, alerts_data):
    map_layers = []

    # ----------------------
    # Disasters Layer
    # ----------------------
    if disasters_data:
        df_disasters = pd.DataFrame(disasters_data)
        if "geo" in df_disasters.columns:
            df_disasters["lat"] = df_disasters["geo"].apply(lambda g: g.get("lat") if isinstance(g, dict) else None)
            df_disasters["lon"] = df_disasters["geo"].apply(lambda g: g.get("lon") if isinstance(g, dict) else None)
            df_disasters = df_disasters.dropna(subset=["lat", "lon"])

            # Color + Weight by severity
            color_map = {"low": [0, 255, 0, 160], "medium": [255, 165, 0, 160], "high": [255, 0, 0, 160]}
            default_color = [200, 30, 0, 160]
            df_disasters["color"] = df_disasters["severity"].apply(lambda x: color_map.get(x, default_color))
            df_disasters["weight"] = df_disasters["severity"].map({"low": 1, "medium": 3, "high": 5}).fillna(1)

            # Scatterplot for discrete points
            map_layers.append(
                pdk.Layer(
                    "ScatterplotLayer",
                    data=df_disasters,
                    get_position="[lon, lat]",
                    get_color="color",
                    get_radius=30000,
                    pickable=True,
                    tooltip=True,
                )
            )

            # Heatmap for severity concentration
            map_layers.append(
                pdk.Layer(
                    "HeatmapLayer",
                    data=df_disasters,
                    get_position="[lon, lat]",
                    get_weight="weight",
                    radiusPixels=60,
                    intensity=1,
                    threshold=0.02,
                )
            )

    # ----------------------
    # Alerts Layer
    # ----------------------
    if alerts_data:
        df_alerts = pd.DataFrame(alerts_data)
        if "location" in df_alerts.columns:
            df_alerts["lat"] = df_alerts["location"].apply(lambda g: g.get("lat") if isinstance(g, dict) else None)
            df_alerts["lon"] = df_alerts["location"].apply(lambda g: g.get("lon") if isinstance(g, dict) else None)
            df_alerts = df_alerts.dropna(subset=["lat", "lon"])

            color_map = {"low": [0, 0, 255, 160], "medium": [0, 128, 255, 160], "high": [0, 255, 255, 160]}
            default_color = [0, 0, 255, 160]
            df_alerts["color"] = df_alerts["severity"].apply(lambda x: color_map.get(x, default_color))

            map_layers.append(
                pdk.Layer(
                    "ScatterplotLayer",
                    data=df_alerts,
                    get_position="[lon, lat]",
                    get_color="color",
                    get_radius=25000,
                    pickable=True,
                    tooltip=True,
                )
            )

    # ----------------------
    # Render Map
    # ----------------------
    if map_layers:
        st.subheader("🗺️ Disaster & Alerts Map")
        st.pydeck_chart(
            pdk.Deck(
                initial_view_state=pdk.ViewState(latitude=20.5937, longitude=78.9629, zoom=4, pitch=30),
                layers=map_layers,
                tooltip={
                    "html": """
                        <b>Title:</b> {title} <br>
                        <b>Type:</b> {disaster_type} <br>
                        <b>Severity:</b> {severity} <br>
                        <b>Published:</b> {publishedAt} <br>
                        <b>Source:</b> {source} <br>
                        <a href='{url}' target='_blank'>🔗 More Info</a>
                    """,
                    "style": {"backgroundColor": "steelblue", "color": "white"}
                }
            )
        )
    else:
        st.info("No geo-location data to display on map.")
