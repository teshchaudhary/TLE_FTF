import streamlit as st
import pandas as pd
import altair as alt

def show_timeline(disasters_data):
    if not disasters_data:
        st.info("No timeline data available.")
        return

    df = pd.DataFrame(disasters_data)
    if "publishedAt" not in df.columns or "severity" not in df.columns:
        st.warning("Timeline data missing required fields.")
        return

    df["publishedAt"] = pd.to_datetime(df["publishedAt"], errors="coerce")
    df = df.dropna(subset=["publishedAt", "severity"])

    # Group by Date + Severity
    timeline = (
        df.groupby([df["publishedAt"].dt.date, "severity"])
        .size()
        .reset_index(name="count")
    )

    chart = (
        alt.Chart(timeline)
        .mark_bar()
        .encode(
            x=alt.X("publishedAt:T", title="Date"),
            y=alt.Y("count:Q", title="Number of Disasters"),
            color=alt.Color("severity:N", legend=alt.Legend(title="Severity")),
            tooltip=["publishedAt:T", "severity:N", "count:Q"],
        )
        .properties(width=900, height=300)
    )

    st.subheader("📈 Disaster Timeline")
    st.altair_chart(chart, use_container_width=True)
