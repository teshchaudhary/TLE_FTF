import streamlit as st
import pandas as pd

def show_alerts_marquee(alerts_data):
    if alerts_data:
        latest_alert = alerts_data[0]  # show the latest alert
        text = f"🚨 Latest Alert: {latest_alert['type'].capitalize()} | Severity: {latest_alert['severity'].capitalize()} | {latest_alert['description']}"
        st.markdown(
            f"""
            <marquee behavior="scroll" direction="left" scrollamount="6" style="
                background: linear-gradient(90deg, #ff0000, #ff6347);
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                border-radius: 8px;">
                🚨 {latest_alert['type'].title()} Alert - {latest_alert['severity'].title()}: {latest_alert['description']}
            </marquee>
            """,
            unsafe_allow_html=True
        )
