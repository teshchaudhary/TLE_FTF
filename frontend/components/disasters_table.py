import streamlit as st
import pandas as pd

def show_table(disasters_data, filters):
    if disasters_data:
        df = pd.DataFrame(disasters_data)

        # Apply filter
        if filters["disaster_severity"] != "All":
            df = df[df["severity"] == filters["disaster_severity"]]

        st.subheader("📋 Disaster List")

        # Reorder & rename columns
        df = df[["title", "disaster_type", "severity", "location", "publishedAt", "source", "url"]]
        df = df.rename(columns={
            "title": "Title",
            "disaster_type": "Type",
            "severity": "Severity",
            "location": "Location",
            "publishedAt": "Published At",
            "source": "Source",
            "url": "URL"
        })

        # Format datetime
        if "Published At" in df.columns:
            df["Published At"] = pd.to_datetime(df["Published At"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M")

        # --- Pagination setup ---
        rows_per_page = 5
        total_pages = (len(df) - 1) // rows_per_page + 1

        if "page" not in st.session_state:
            st.session_state.page = 1

        page = st.session_state.page
        start = (page - 1) * rows_per_page
        end = start + rows_per_page
        df_page = df.iloc[start:end]

        # --- Custom Dark Table Styling ---
        st.markdown("""
            <style>
            .dark-table {
                width: 100%;
                border-collapse: collapse;
                background-color: #1E1E1E;
                color: white;
                border-radius: 10px;
                overflow: hidden;
            }
            .dark-table th, .dark-table td {
                border: 1px solid #444;
                padding: 8px 12px;
                text-align: left;
                max-width: 200px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .dark-table th {
                background-color: #333;
                font-weight: bold;
            }
            .dark-table tr:nth-child(even) {
                background-color: #2A2A2A;
            }
            .dark-table tr:hover {
                background-color: #444;
            }
            </style>
        """, unsafe_allow_html=True)

        # Show table
        df_html = df_page.to_html(classes="dark-table", index=False, escape=False)
        st.markdown(df_html, unsafe_allow_html=True)

        # --- Pagination Controls BELOW table ---
        col1, col2, col3 = st.columns([1,3,1])
        with col1:
            if st.button("⬅️ Prev") and page > 1:
                st.session_state.page -= 1
        with col2:
            st.markdown(f"<div style='text-align:center;'>Page {page} of {total_pages}</div>", unsafe_allow_html=True)
        with col3:
            if st.button("Next ➡️") and page < total_pages:
                st.session_state.page += 1

    else:
        st.info("No disasters found.")
