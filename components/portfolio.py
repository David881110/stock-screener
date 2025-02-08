import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import load_latest_portfolio

# 📊 Balkendiagramm für gewichtete Portfolio-Faktoren
def plot_weighted_factors(weighted_scores, title):
    factors = ["Wachstum", "Bewertung", "Qualität", "Volatilität", "Momentum"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(factors, weighted_scores)

    for bar, value in zip(bars, weighted_scores):
        bar.set_color("green" if value > 0 else "red")
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{value:.2f}', ha='center', va='bottom' if value > 0 else 'top')

    ax.axhline(0, color='black', linewidth=1)
    ax.set_ylabel("Faktor-Score")
    ax.set_title(title)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# 📈 Portfolioanalyse UI
def show_portfolio_analysis():
    st.header("📊 Portfolioanalyse")

    portfolio_df = load_latest_portfolio()

    # 📌 Auswahl der Aktien
    selected_stocks = st.multiselect("Wähle deine Aktien:", portfolio_df["Unternehmensname"].unique())

    if selected_stocks:
        selected_df = portfolio_df[portfolio_df["Unternehmensname"].isin(selected_stocks)].copy()

        st.markdown("### 📊 Gewichtung der ausgewählten Aktien")
        weights = {}

        # 🚀 Gleichverteilung der Gewichte (standardmäßig 100%)
        default_weight = round(100 / len(selected_stocks), 2)

        col1, col2 = st.columns(2)
        total_weight = 0

        # 📊 Eingabe der Gewichte
        for stock in selected_stocks:
            weight = col1.number_input(
                f"📈 Gewicht für {stock} (%)",
                min_value=0.0,
                max_value=100.0,
                value=default_weight,
                step=0.1,
                key=stock
            )
            weights[stock] = weight
            total_weight += weight

        # 🔔 Hinweis, falls die Summe ≠ 100%
        if round(total_weight, 2) != 100:
            st.warning(f"⚠️ Die Summe der Gewichte beträgt {round(total_weight, 2)}%. Bitte auf 100% anpassen.")

        # 📊 Berechnung der gewichteten Faktor-Scores
        if st.button("✅ Portfolioanalyse starten"):
            normalized_weights = {stock: w / 100 for stock, w in weights.items()}

            factor_columns = ["Final Growth Score", "Value Score", "Quality Score", "Min Volatility Score", "Composite Momentum Score"]

            weighted_scores = selected_df[factor_columns].multiply(list(normalized_weights.values()), axis=0).sum()

            # 📈 Darstellung der gewichteten Faktoren
            plot_weighted_factors(weighted_scores, "Gewichtete Portfolio-Faktoren")

