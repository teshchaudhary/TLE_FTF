import streamlit as st
import pandas as pd

def show_table(disasters_data, filters):
    if disasters_data:
        df = pd.DataFrame(disasters_data)
        if filters["disaster_severity"] != "All":
            df = df[df["severity"] == filters["disaster_severity"]]
        st.subheader("📋 Disaster List")
        st.dataframe(
            df[["title","disaster_type","severity","location","publishedAt","source","url"]],
            width='stretch', height=400
        )
    else:
        st.info("No disasters found.")
