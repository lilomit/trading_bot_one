import pandas as pd
import ta

def calculate_rsi(df, window=14):
    df = df.copy()

    # اطمینان از وجود ستون Close
    if 'Close' not in df.columns:
        raise ValueError("❌ Error: 'Close' column not found in DataFrame")

    # اطمینان از اینکه Series و عددی باشه
    close = df['Close']
    if isinstance(close, pd.DataFrame):
        close = close.squeeze()

    close = pd.to_numeric(close, errors='coerce')
    df['Close'] = close  # آپدیت دیتافریم اصلی
    df.dropna(subset=['Close'], inplace=True)

    if close.empty or close.isna().all():
        raise ValueError("❌ Error: 'Close' column is empty or full of NaNs after cleaning.")

    # محاسبه RSI
    rsi = ta.momentum.RSIIndicator(close=close, window=window).rsi()
    df['RSI'] = rsi

    return df


def calculate_supertrend(df, period=10, multiplier=3):
    df = df.copy()

    # بررسی ستون‌های مورد نیاز
    for col in ['High', 'Low', 'Close']:
        if col not in df.columns:
            raise ValueError(f"❌ Error: '{col}' column not found in DataFrame")

        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(subset=['High', 'Low', 'Close'], inplace=True)

    if df.empty:
        raise ValueError("❌ Error: DataFrame is empty after cleaning High/Low/Close.")

    # محاسبه ATR
    atr = ta.volatility.AverageTrueRange(
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        window=period
    ).average_true_range()

    hl2 = (df['High'] + df['Low']) / 2
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    supertrend = [True]
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > upperband.iloc[i - 1]:
            supertrend.append(True)
        elif df['Close'].iloc[i] < lowerband.iloc[i - 1]:
            supertrend.append(False)
        else:
            supertrend.append(supertrend[-1])

    df['Supertrend'] = supertrend

    return df