import streamlit as st
from datetime import datetime

def show_filters():
    st.sidebar.header("🔎 Search Filters")

    q = st.sidebar.text_input("Keyword")
    disaster_type = st.sidebar.selectbox("Disaster Type", ["All","earthquake","flood","cyclone","wildfire","tsunami"])
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

    if st.sidebar.button("⚡ Fetch Latest News"):
        with st.spinner("Fetching and indexing..."):
            import sys, os
            sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
            
            import fetch_and_index
            import reddit

            # Pass limit=5 and query="disaster" when triggered from Streamlit
            fetch_and_index.main(limit=5, query="disaster")
            reddit.main(limit=5, query="disaster")

        st.success("✅ Latest news & Reddit posts fetched!")

    return {
        "q": q,
        "disaster_type": disaster_type,
        "disaster_severity": disaster_severity,
        "alert_severity": alert_severity,
        "location": location,
        "date_range": date_range,
        "limit": limit
    }
