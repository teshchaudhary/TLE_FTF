import streamlit as st
from components import filters, disasters_table, alerts_marquee, timeline_chart, map_view, legend
from utils import fetch_disasters, fetch_alerts

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="🌍 Disaster Monitor", layout="wide")
st.title("🌍 Disaster Monitor Dashboard")

# ----------------------
# Sidebar Filters
# ----------------------
filter_params = filters.show_filters()

# ----------------------
# Fetch Data
# ----------------------
disasters_data = fetch_disasters(API_URL, filter_params)
alerts_data = fetch_alerts(API_URL, filter_params)

# ----------------------
# Alerts Marquee
# ----------------------
alerts_marquee.show_alerts_marquee(alerts_data)

st.markdown("---")

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

# ----------------------
# Map
# ----------------------
map_view.show_map(disasters_data, alerts_data)
