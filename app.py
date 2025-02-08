import streamlit as st
from components import optimizer, screener, portfolio

# App-Konfiguration
st.set_page_config(layout="centered", page_title="📊 Factor Investing Tool")

# Sidebar Navigation
menu = st.sidebar.radio("📋 Navigation", ["🏠 Startseite", "📊 Portfolioanalyse", "📈 Screener", "⚙️ Optimizer"])

# Dynamisches Laden der Features
if menu == "📊 Portfolioanalyse":
    portfolio.show_portfolio_analysis()

elif menu == "📈 Screener":
    screener.show_screener()

elif menu == "⚙️ Optimizer":
    optimizer.show_optimizer()

else:
    st.title("📊 Factor Investing Tool")
    st.write("Willkommen zur Analyse-App!")
