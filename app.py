import streamlit as st
from components import screener

# **🔹 Streamlit Konfiguration**
st.set_page_config(layout="wide", page_title="📊 Aktien-Screener")

# **🔹 Starte sofort den Screener**
screener.show_screener()
