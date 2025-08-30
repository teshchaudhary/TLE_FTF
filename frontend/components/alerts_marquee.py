import streamlit as st

def show_alerts_marquee(alerts_data):
    if alerts_data:
        latest_alert = alerts_data[0]  # show the latest alert
        alert_type = latest_alert['type'].capitalize()
        severity = latest_alert['severity'].capitalize()
        description = latest_alert['description']

        st.markdown(
            f"""
            <style>
            @keyframes blinker {{
                50% {{ opacity: 0; }}
            }}
            .blinking {{
                animation: blinker 1s linear infinite;
            }}
            </style>

            <marquee behavior="scroll" direction="left" scrollamount="6" style="
                background: linear-gradient(90deg, #ff0000, #ff4500, #ff6347);
                color: white;
                font-size: 17px;
                font-weight: bold;
                padding: 10px;
                border-radius: 8px;
                letter-spacing: 0.5px;">
                <span class="blinking">🚨</span>
                <b>{alert_type} Alert</b> | Severity: <b>{severity}</b> | {description}
                <span class="blinking">🚨</span>
            </marquee>
            """,
            unsafe_allow_html=True
        )
