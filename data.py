import yfinance as yf
import pandas as pd

def get_data(ticker='BTC-USD', interval='5m', period='20d'):
    """
    دریافت داده‌ها از yfinance با پارامترهای تیکر، تایم‌فریم و دوره
    """
    df = yf.download(ticker, interval=interval, period=period, auto_adjust=False)

    # اگر MultiIndex هست، ستون‌ها رو به تک‌لایه تبدیل کنیم
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # فقط ستون‌های مورد نیاز
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.dropna(inplace=True)
    return df

def convert_interval_to_pandas_freq(interval):
    """
    تبدیل فرمت تایم‌فریم ورودی به فرمت مناسب pandas resample
    مثل: 5T -> 5min، 1H -> 1h، 1D -> 1d
    """
    interval = interval.upper()
    if interval.endswith('T'):
        # 'T' دقیقه است، به 'min' تبدیل شود
        return interval[:-1] + 'min'
    elif interval.endswith('H'):
        # 'H' ساعت است، به 'h' تبدیل شود
        return interval[:-1] + 'h'
    elif interval.endswith('D'):
        # روزانه
        return interval[:-1] + 'd'
    else:
        # اگر فرمت ناشناخته بود، همان مقدار را برگردان
        return interval

def resample_data(df, new_interval):
    """
    تبدیل داده‌ها به تایم‌فریم جدید با resampling پانداس
    new_interval: str مثل '5T' برای 5 دقیقه، '15T'، '1H'، '1D'
    """
    if df is None or df.empty:
        return df

    # ابتدا ایندکس باید DatetimeIndex باشد
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, errors='coerce')
        df.dropna(inplace=True)
    
    # تبدیل فرمت تایم فریم به فرمت pandas
    pandas_freq = convert_interval_to_pandas_freq(new_interval)

    df_resampled = pd.DataFrame()
    df_resampled['Open'] = df['Open'].resample(pandas_freq).first()
    df_resampled['High'] = df['High'].resample(pandas_freq).max()
    df_resampled['Low'] = df['Low'].resample(pandas_freq).min()
    df_resampled['Close'] = df['Close'].resample(pandas_freq).last()
    df_resampled['Volume'] = df['Volume'].resample(pandas_freq).sum()

    df_resampled.dropna(inplace=True)
    return df_resampled