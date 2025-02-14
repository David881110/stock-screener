import streamlit as st
import pandas as pd
import plotly.graph_objects as go  # 🎯 Interaktive Diagramme mit Plotly
from utils import load_latest_portfolio

# **📌 Mapping der Faktoren zu DataFrame-Spalten**
FACTOR_MAPPING = {
    "Wachstum": "Final Growth 0-100",
    "Qualität": "Final Quality 0-100",
    "Bewertung": "Final Value 0-100",
    "Trendstärke": "Final Momentum 0-100",
    "Kursstabilität": "Final Min_Vol 0-100"
}

# **📌 Detailanalyse-Faktoren**
VALUE_FACTORS = {
    "Gewinnrendite": "EarningsYield 0-100",
    "klassische Bewertung": "Valuation 0-100"
}

GROWTH_FACTORS = {
    "historisches Gewinnwachstum": "Earnings Growth 0-100",
    "historisches Umsatzwachstum": "Sales Growth 0-100",
    "prognostiziertes Gewinnwachstum": "EPS Growth 0-100"
}

TRENDSTÄRKE_FACTORS = {
    "Momentum 12 Monate": "Momentum12M 0-100",
    "Momentum 6 Monate": "Momentum6M 0-100"
}

QUALITY_FACTORS = {
    "Stabilität": "Variability 0-100",
    "Profitabilität": "Profitability 0-100",
    "Verschuldung": "Leverage 0-100"
}

KURSSTABILITÄT_FACTORS = {
    "Kursstabilität": "Final Min_Vol 0-100"
}

# **📊 Interaktives Balkendiagramm für einzelne Aktien**
def plot_factors(stock_data, selected_factors):
    factor_scores = {factor: round(stock_data[column]) for factor, column in FACTOR_MAPPING.items() if factor in selected_factors}
    factor_names, scores = zip(*factor_scores.items()) if factor_scores else ([], [])

    fig = go.Figure()
    fig.add_trace(go.Bar(y=factor_names, x=[100] * len(scores), orientation='h', marker=dict(color="lightgray", opacity=0.5), width=0.6, hoverinfo="none"))
    fig.add_trace(go.Bar(y=factor_names, x=scores, orientation='h', marker=dict(color="green"), 
                         text=[f"{score}%" for score in scores], textposition="inside", 
                         textfont=dict(size=20), hoverinfo="text", width=0.6))

    fig.update_layout(
        xaxis=dict(tickvals=[0, 50, 100], ticktext=["Unattraktiv", "Neutral", "Attraktiv"], range=[0, 100]),
        yaxis=dict(title="", tickfont=dict(size=18), categoryorder="array", categoryarray=factor_names, dtick=0.5),
        barmode="overlay", height=max(200, 50 * len(factor_names)), width=st.session_state["screen_width"] * 0.8, showlegend=False,
        margin=dict(l=0, r=0, t=0, b=50)
    )

    return fig

# **📈 Interaktiver Donut-Chart für Gesamtbewertung**
def plot_average_pie(stock_data, selected_factors):
    selected_columns = [FACTOR_MAPPING[factor] for factor in selected_factors]
    selected_scores = [round(stock_data[col]) for col in selected_columns] if selected_columns else []
    
    average_score = round(sum(selected_scores) / len(selected_scores)) if selected_scores else 0

    fig = go.Figure()
    fig.add_trace(go.Pie(labels=["Total", ""], values=[average_score, 100 - average_score], marker=dict(colors=["green", "lightgray"]), hole=0.6, textinfo="none", hoverinfo="label+percent"))
    fig.add_annotation(text=f"<b>Total</b><br><span style='font-size:28px;'>{average_score}%</span>", 
                       showarrow=False, x=0.5, y=0.5, xref="paper", yref="paper", font=dict(size=22, color="black"), align="center")

    fig.update_layout(height=200, width=250, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
    return fig

# **📊 Detailanalyse**
def plot_detail_analysis(stock_data):
    categories = {
        "Value-Faktoren": VALUE_FACTORS,
        "Wachstums-Faktoren": GROWTH_FACTORS,
        "Trendstärke-Faktoren": TRENDSTÄRKE_FACTORS,
        "Qualitäts-Faktoren": QUALITY_FACTORS,
        "Kursstabilität": KURSSTABILITÄT_FACTORS
    }

    fig = go.Figure()

    for category, factors in categories.items():
        factor_names, values = zip(*{factor: round(stock_data[column]) for factor, column in factors.items()}.items())
        fig.add_trace(go.Bar(y=factor_names, x=[100] * len(values), orientation='h', marker=dict(color="lightgray", opacity=0.5), width=0.6))
        fig.add_trace(go.Bar(y=factor_names, x=values, orientation='h', marker=dict(color="blue" if category == "Value-Faktoren" else 
                        "orange" if category == "Wachstums-Faktoren" else 
                        "red" if category == "Trendstärke-Faktoren" else 
                        "purple" if category == "Qualitäts-Faktoren" else "green"),
                        text=[f"{score}%" for score in values], textposition="inside", 
                        textfont=dict(size=20), hoverinfo="text", width=0.6))

    fig.update_layout(
        xaxis=dict(tickvals=[0, 50, 100], ticktext=["Unattraktiv", "Neutral", "Attraktiv"], range=[0, 100]),
        yaxis=dict(title="", tickfont=dict(size=18), dtick=0.5),
        barmode="overlay", height=500, width=st.session_state["screen_width"] * 0.8, showlegend=False,
        margin=dict(l=0, r=0, t=0, b=50)
    )

    return fig

# **📈 Screener UI**
def show_screener():
    st.header("📈 Aktien-Screener")

    if "screen_width" not in st.session_state:
        st.session_state["screen_width"] = 800

    portfolio_df = load_latest_portfolio()
    portfolio_df = portfolio_df.dropna(subset=FACTOR_MAPPING.values())

    selected_stock = st.selectbox("Wähle eine Aktie:", portfolio_df["Unternehmensname"].unique())

    if selected_stock:
        stock_data = portfolio_df[portfolio_df["Unternehmensname"] == selected_stock].iloc[0]

        st.subheader("🔍 Wähle relevante Faktoren:")
        cols = st.columns(5)
        factors = {factor: cols[i].checkbox(factor, value=True) for i, factor in enumerate(FACTOR_MAPPING.keys())}
        selected_factors = [name for name, checked in factors.items() if checked]

        if not selected_factors:
            st.error("⚠️ Mindestens 1 Faktor muss ausgewählt werden!")
            return

        st.markdown(f"<h4 style='text-align: center; font-weight: bold; font-size:18px;'>Faktoranalyse der {selected_stock}-Aktie</h4>", unsafe_allow_html=True)

        col1, col2 = st.columns([4, 1])
        with col1:
            st.plotly_chart(plot_factors(stock_data, selected_factors), use_container_width=True)
        with col2:
            st.plotly_chart(plot_average_pie(stock_data, selected_factors), use_container_width=True)

        if st.button("📊 Detailanalyse starten", use_container_width=True):
            st.subheader("🔍 Detailanalyse nach Kategorien")
            st.plotly_chart(plot_detail_analysis(stock_data), use_container_width=True)

        if st.button("📊 Top Aktien deiner gewählten Faktoren anzeigen", use_container_width=True):
            portfolio_df["Total Score"] = portfolio_df[[FACTOR_MAPPING[f] for f in selected_factors]].mean(axis=1)
            top_stocks = portfolio_df.nlargest(50, "Total Score")[["ISIN", "Unternehmensname", "Total Score", "Sektor"]]
            st.subheader("📊 Top 50 Aktien nach Gesamtbewertung")
            st.dataframe(top_stocks, hide_index=True)

    st.markdown("---")
