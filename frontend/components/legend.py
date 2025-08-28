import streamlit as st

def show_legend():
    st.markdown(
        """
        **Map Legend:**  
        <span style="color:#FF0000">■</span> Disaster (High)  
        <span style="color:#FFA500">■</span> Disaster (Medium)  
        <span style="color:#00FF00">■</span> Disaster (Low)  
        <span style="color:#0000FF">■</span> Alert
        """,
        unsafe_allow_html=True
    )
