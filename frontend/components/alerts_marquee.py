import streamlit as st

def show_alerts_marquee(alerts_data, max_alerts=3):
    """
    Displays the latest alerts in a scrolling marquee.
    Args:
        alerts_data (list): List of alert dictionaries
        max_alerts (int): How many latest alerts to show
    """
    if alerts_data:
        # Take latest N alerts
        latest_alerts = alerts_data[:max_alerts]

        # Build HTML for scrolling marquee
        marquee_html = '<marquee behavior="scroll" direction="left" scrollamount="6" style="padding:10px; border-radius:8px; background: linear-gradient(90deg, #ff4d4d, #ff9999); font-weight:bold; font-size:18px;">'

        for alert in latest_alerts:
            color = "white"
            if alert["severity"].lower() == "low":
                color = "#00FF00"
            elif alert["severity"].lower() == "medium":
                color = "#FFA500"
            elif alert["severity"].lower() == "high":
                color = "#FF0000"

            text = f'<span style="color:{color}; margin-right:50px;">🚨 {alert["type"].title()} ({alert["severity"].title()}): {alert["description"]}</span>'
            marquee_html += text

        marquee_html += "</marquee>"

        st.markdown(marquee_html, unsafe_allow_html=True)
    else:
        st.info("No alerts to display.")
