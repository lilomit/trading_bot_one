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

def resample_data(df, new_interval):
    """
    تبدیل داده‌ها به تایم‌فریم جدید با resampling پانداس
    new_interval: str مثل '5T' برای 5 دقیقه، '15T'، '1H'، '1D'
    """
    df_resampled = pd.DataFrame()

    df_resampled['Open'] = df['Open'].resample(new_interval).first()
    df_resampled['High'] = df['High'].resample(new_interval).max()
    df_resampled['Low'] = df['Low'].resample(new_interval).min()
    df_resampled['Close'] = df['Close'].resample(new_interval).last()
    df_resampled['Volume'] = df['Volume'].resample(new_interval).sum()

    df_resampled.dropna(inplace=True)
    return df_resampled