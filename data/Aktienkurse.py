import yfinance as yf
import pandas as pd
import time
import random

# Lade die Ticker aus ticker2.csv
tickers_df = pd.read_csv('ticker2.csv')
tickers = tickers_df['Ticker'].dropna().unique().tolist()

# Definierte Währungen
currencies = ['DKK', 'CHF', 'GBP', 'JPY', 'CAD', 'AUD', 'HKD', 'SGD', 'SEK', 'NOK', 'ILS', 'NZD', 'EUR', 'USD']

# Abfrage der Wechselkurse
exchange_rates = {}
for currency in currencies:
    if currency != 'USD':
        try:
            rate = yf.download(f'{currency}USD=X', period='1d')['Close'].dropna().iloc[-1]
            exchange_rates[currency] = rate
        except Exception as e:
            print(f"Fehler beim Abrufen des Wechselkurses für {currency}: {e}")
            exchange_rates[currency] = None
    else:
        exchange_rates['USD'] = 1  # USD zu USD ist 1:1

# Initialisiere die Datenliste
data = []

# Lade die Aktienkurse für jeden Ticker
for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        
        # Abrufen des zuletzt verfügbaren Schlusskurses
        hist = stock.history(period="5d")  # Abruf der letzten 5 Tage
        if hist.empty:
            raise ValueError(f"Keine historischen Daten für Ticker: {ticker}")

        last_close = hist['Close'].dropna().iloc[-1]
        info = stock.info
        currency = info.get('currency')

        if last_close is None or currency is None:
            raise ValueError(f"Fehlende Preisinformationen für Ticker: {ticker}")

        # Umrechnung in USD
        if currency == 'USD':
            price_in_usd = last_close
        elif currency in exchange_rates and exchange_rates[currency] is not None:
            price_in_usd = last_close * exchange_rates[currency]  # Multiplikation statt Division
        else:
            raise ValueError(f"Wechselkurs für {currency} nicht verfügbar")

        # Umrechnung in EUR
        if currency == 'EUR':
            price_in_eur = last_close
        elif 'EUR' in exchange_rates and exchange_rates['EUR'] is not None:
            price_in_eur = price_in_usd / exchange_rates['EUR']
        else:
            raise ValueError("Wechselkurs für EUR nicht verfügbar")

        # Speichere die Daten
        data.append({
            'Ticker': ticker,
            'Aktienkurs': round(last_close, 2),
            'Währung': currency,
            'Aktienkurs in EUR': round(price_in_eur, 2),
            'Aktienkurs in USD': round(price_in_usd, 2)
        })

        # Vermeide Rate-Limit-Fehler
        time.sleep(random.uniform(1, 2))

    except Exception as e:
        print(f"Fehler bei {ticker}: {e}")

# Speichere die Daten in eine CSV-Datei
aktuelle_kurse_df = pd.DataFrame(data)
aktuelle_kurse_df.to_csv('aktuelleKurse.csv', index=False)

print("✅ Daten wurden in aktuelleKurse.csv gespeichert")
