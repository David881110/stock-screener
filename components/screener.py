import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import load_latest_portfolio

# 📊 Balkendiagramm für einzelne Aktien
def plot_factors(stock_data, title):
    factors = {
        "Wachstum": stock_data["Final Growth Score"],
        "Bewertung": stock_data["Value Score"],
        "Qualität": stock_data["Quality Score"],
        "Volatilität": stock_data["Min Volatility Score"],
        "Momentum": stock_data["Composite Momentum Score"]
    }

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(factors.keys(), factors.values())

    # Farbe je nach Wert
    for bar, value in zip(bars, factors.values()):
        bar.set_color("green" if value > 0 else "red")
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{value:.2f}', ha='center', va='bottom')

    ax.axhline(0, color='black', linewidth=1)
    ax.set_ylabel("Faktor-Score")
    ax.set_title(title)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# 📈 Screener UI
def show_screener():
    st.header("📈 Aktien-Screener")

    portfolio_df = load_latest_portfolio()

    # 🎯 Auswahl einzelner Aktie
    selected_stock = st.selectbox("Wähle eine Aktie:", portfolio_df["Unternehmensname"].unique())
    if selected_stock:
        stock_data = portfolio_df[portfolio_df["Unternehmensname"] == selected_stock].iloc[0]
        plot_factors(stock_data, f"Faktor-Analyse für {selected_stock}")

    st.markdown("---")

    # 🔍 Vordefinierte Screener
    st.subheader("📊 Vordefinierte Screener (Top 10)")

    screener_options = {
        "Top Wachstumsaktien": "Final Growth Score",
        "Top Value Aktien": "Value Score",
        "Top Qualitätsaktien": "Quality Score",
        "Top Momentum Aktien": "Composite Momentum Score",
        "Top Minimum Varianz Aktien": "Min Volatility Score"
    }

    selected_screener = st.radio("Wähle einen Screener:", list(screener_options.keys()))

    if selected_screener:
        factor_column = screener_options[selected_screener]

        # 📋 Top 10 Aktien nach gewähltem Faktor
        top_stocks = portfolio_df.nlargest(10, factor_column)
        selected_top_stock = st.selectbox(f"Wähle eine Aktie aus den {selected_screener}:", top_stocks["Unternehmensname"])

        st.dataframe(top_stocks[["Unternehmensname", factor_column]])

        # 📊 Balkendiagramm für ausgewählte Aktie aus Screener
        if selected_top_stock:
            stock_data = top_stocks[top_stocks["Unternehmensname"] == selected_top_stock].iloc[0]
            plot_factors(stock_data, f"Faktor-Analyse für {selected_top_stock}")
