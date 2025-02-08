import streamlit as st
import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
from scipy.optimize import minimize

def load_portfolio_data():
    """Lädt das neueste Portfolio-Dataset."""
    portfolio_files = glob.glob("data/portfolio_*.csv")
    if not portfolio_files:
        st.error("Keine Portfolio-Dateien gefunden.")
        return None
    latest_file = max(portfolio_files, key=os.path.getctime)
    return pd.read_csv(latest_file)

def optimize_portfolio(portfolio_df, min_stocks, max_stocks, allowed_sectors, target_factor):
    """
    Optimiert das Portfolio, indem es den ausgewählten Faktor maximiert, während die anderen Faktoren
    zwischen -0.1 und 0.1 gehalten werden.
    """
    if portfolio_df is None or portfolio_df.empty:
        return None, None
    
    # Filter nach erlaubten Sektoren
    if allowed_sectors:
        portfolio_df = portfolio_df[portfolio_df['Sektor'].isin(allowed_sectors)]
    
    # Faktor-Spalten definieren
    factor_columns = {
        "Growth": "Final Growth Score",
        "Value": "Value Score",
        "Quality": "Quality Score",
        "Minimum Volatility": "Min Volatility Score",
        "Momentum": "Composite Momentum Score"
    }
    
    if target_factor not in factor_columns:
        st.error("Ungültige Optimierungsstrategie.")
        return None, None
    
    # Sortiere nach Ziel-Faktor und wähle die besten Aktien
    sorted_df = portfolio_df.sort_values(by=factor_columns[target_factor], ascending=False)
    selected_stocks = sorted_df.head(max_stocks)
    if len(selected_stocks) < min_stocks:
        return None, None
    
    # Definiere Zielfunktion für Optimierung
    def objective(weights):
        portfolio_scores = np.dot(weights, selected_stocks[factor_columns[target_factor]])
        return -portfolio_scores  # Negatives Vorzeichen, da wir maximieren wollen
    
    # Nebenbedingungen: Andere Faktoren zwischen -0.1 und 0.1 halten
    constraints = []
    for factor, column in factor_columns.items():
        if factor != target_factor:
            constraints.append({
                'type': 'ineq',
                'fun': lambda w, col=column: 0.25 - abs(np.dot(w, selected_stocks[col]))
            })
    
    # Gleichheitsbedingung: Summe der Gewichte = 1
    constraints.append({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
    
    # Grenzen für Gewichte (mindestens 0, maximal 1)
    num_selected_stocks = len(selected_stocks)
    bounds = [(0, 1)] * num_selected_stocks
    
    # Initiale Gewichte gleichverteilt
    initial_weights = np.ones(num_selected_stocks) / num_selected_stocks
    
    # Optimierung durchführen
    result = minimize(objective, initial_weights, bounds=bounds, constraints=constraints)
    
    if not result.success:
        return None, None
    
    selected_stocks = selected_stocks.iloc[:num_selected_stocks].copy()
    selected_stocks["Weight"] = result.x * 100  # Gewichtung in %
    avg_factors = selected_stocks[factor_columns.values()].multiply(selected_stocks["Weight"] / 100, axis=0).sum()
    
    return selected_stocks, avg_factors

def plot_factors(avg_factors, title):
    """Erstellt ein Balkendiagramm für die Faktoren."""
    factors = ["Growth", "Value", "Quality", "Volatility", "Momentum"]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(factors, avg_factors, color=["blue", "green", "red", "purple", "orange"])
    ax.set_ylabel("Durchschnittlicher Faktorwert")
    ax.set_title(title)
    st.pyplot(fig)

def show_optimizer():
    """Streamlit-Oberfläche für den Optimizer."""
    st.subheader("⚙️ Portfolio Optimizer")
    
    portfolio_df = load_portfolio_data()
    if portfolio_df is None:
        return
    
    min_stocks = st.number_input("Minimale Anzahl verschiedener Aktien", min_value=1, max_value=20, value=3)
    max_stocks = st.number_input("Maximale Anzahl verschiedener Aktien", min_value=min_stocks, max_value=20, value=10)
    allowed_sectors = st.multiselect("Zugelassene Sektoren", portfolio_df["Sektor"].unique(), default=list(portfolio_df["Sektor"].unique()))
    
    st.subheader("Optimierungsmodus wählen")
    optimization_mode = st.radio(
        "Welche Optimierung soll durchgeführt werden?",
        ["Growth", "Value", "Quality", "Minimum Volatility", "Momentum"]
    )
    
    if st.button("🔍 Optimales Portfolio berechnen"):
        optimized_portfolio, avg_factors = optimize_portfolio(portfolio_df, min_stocks, max_stocks, allowed_sectors, optimization_mode)
        
        if optimized_portfolio is not None:
            st.write(f"📊 Optimales {optimization_mode}-Portfolio mit Gewichtungen:")
            st.dataframe(optimized_portfolio[["Ticker", "Unternehmensname", "Sektor", "Weight"]], hide_index=True)
            
            st.write("### Durchschnittliche Faktorwerte des optimierten Portfolios:")
            st.write(avg_factors)
            
            plot_factors(avg_factors, f"Faktorverteilung für das {optimization_mode}-Portfolio")
        else:
            st.warning("⚠️ Kein Portfolio erfüllt die Kriterien. Bitte passen Sie Ihre Auswahl an.")
