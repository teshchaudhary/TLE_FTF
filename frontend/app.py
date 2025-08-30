import streamlit as st
from components import filters, disasters_table, alerts_marquee, timeline_chart, map_view, legend
from utils import fetch_disasters, fetch_alerts
from streamlit_autorefresh import st_autorefresh

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="🌍 Disaster Monitor", layout="wide")
st.title("🌍 Disaster Monitor Dashboard")

# ----------------------
# Sidebar Filters
# ----------------------
filter_params = filters.show_filters()

# ----------------------
# Auto-refresh every 10 seconds
# ----------------------
st_autorefresh(interval=10000, key="auto_refresh")

# ----------------------
# Alerts Marquee
# ----------------------
alerts_data = fetch_alerts(API_URL, filter_params)
alerts_marquee.show_alerts_marquee(alerts_data)
st.markdown("---")

# ----------------------
# Fetch Disasters
# ----------------------
disasters_data = fetch_disasters(API_URL, filter_params)

# ----------------------
# Disaster Table
# ----------------------
disasters_table.show_table(disasters_data, filter_params)
st.markdown("---")

# ----------------------
# Timeline Chart
# ----------------------
timeline_chart.show_timeline(disasters_data)
st.markdown("---")

# ----------------------
# Map Legend
# ----------------------
legend.show_legend()
st.markdown("---")

# ----------------------
# Map View
# ----------------------
map_view.show_map(disasters_data, alerts_data)
