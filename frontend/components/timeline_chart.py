import streamlit as st
import pandas as pd
import altair as alt

def show_timeline(disasters_data):
    if not disasters_data:
        st.info("No timeline data available.")
        return

    df = pd.DataFrame(disasters_data)
    df["publishedAt"] = pd.to_datetime(df["publishedAt"])
    timeline = df.groupby([df["publishedAt"].dt.date, "severity"]).size().reset_index(name="count")

    chart = alt.Chart(timeline).mark_bar().encode(
        x="publishedAt:T",
        y="count:Q",
        color="severity:N",
        tooltip=["publishedAt:T", "severity:N", "count:Q"],
    ).properties(width=900, height=300)

    st.subheader("📈 Disaster Timeline")
    st.altair_chart(chart, use_container_width=True)
