import yfinance as yf
import pandas as pd

def get_data(ticker='BTC-USD', interval='5m', period='20d'):
    df = yf.download(ticker, interval=interval, period=period, auto_adjust=False)

    # اگر MultiIndex هست، ستون‌ها رو به تک‌لایه تبدیل کنیم
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # فقط ستون‌های مورد نیاز
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.dropna(inplace=True)
    return df