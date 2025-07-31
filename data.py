import yfinance as yf
import pandas as pd

def get_data(ticker='BTC-USD', interval='5m', period='20d'):
    df = yf.download(ticker, interval=interval, period=period, auto_adjust=False)
    # فقط ستون‌های مورد نیاز
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.dropna(inplace=True)
    return df
