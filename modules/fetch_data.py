import yfinance as yf
import pandas as pd

def clean_ticker_input(ticker_str):
    tickers = [t.strip().upper() for t in ticker_str.split(',') if t.strip()]
    return list(dict.fromkeys(tickers))  # Removes duplicates, keeps order

def fetch_price_data(ticker, start_date, end_date):
    data = yf.download(ticker, interval='1mo', auto_adjust=False, start=start_date, end=end_date)
    return data['Adj Close'] if not data.empty else pd.Series(dtype='float64')

def get_all_data(ticker_list, start_date, end_date):
    price_data = {}
    return_data = {}
    for ticker in ticker_list:
        prices = fetch_price_data(ticker, start_date, end_date)
        if not prices.empty:
            price_data[ticker] = prices
            return_data[ticker] = prices.pct_change().dropna()
    return price_data, return_data
