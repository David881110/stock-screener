import pandas as pd
import glob
import os

def load_latest_portfolio():
    files = glob.glob('data/portfolio_*.csv')
    latest_file = max(files, key=os.path.getctime)
    return pd.read_csv(latest_file)

def load_stock_prices():
    return pd.read_csv('data/aktuelleKurse.csv')
