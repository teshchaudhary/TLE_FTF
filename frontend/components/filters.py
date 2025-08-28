import streamlit as st
from datetime import datetime

def show_filters():
    st.sidebar.header("🔎 Search Filters")

    q = st.sidebar.text_input("Keyword")

    disaster_type_options = ["All", "earthquake", "flood", "cyclone", "wildfire", "tsunami"]
    disaster_type = st.sidebar.selectbox("Disaster Type", disaster_type_options)

    severity_options = ["All", "low", "medium", "high"]
    disaster_severity = st.sidebar.selectbox("Disaster Severity", severity_options)
    alert_severity = st.sidebar.selectbox("Alert Severity", severity_options)

    location = st.sidebar.text_input("Location")

    all_dates = st.sidebar.checkbox("All Dates", value=True)
    if not all_dates:
        date_range = st.sidebar.date_input("Published Date Range",
                                           value=[datetime(2023,1,1), datetime.today()])
    else:
        date_range = None

    limit = st.sidebar.slider("Max Results", 10, 200, 50)

    # Button to trigger ingestion
    if st.sidebar.button("⚡ Fetch Latest News"):
        st.session_state["fetch_news"] = True

    return {
        "q": q,
        "disaster_type": disaster_type,
        "disaster_severity": disaster_severity,
        "alert_severity": alert_severity,
        "location": location,
        "date_range": date_range,
        "limit": limit
    }
