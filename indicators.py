import pandas as pd
import ta

def calculate_rsi(df, window=14):
    """
    محاسبه RSI و اضافه کردن آن به DataFrame
    پارامترها:
    - df: DataFrame ورودی حاوی ستون 'Close'
    - window: طول پنجره RSI (پیش‌فرض 14)
    
    خروجی:
    DataFrame با ستون جدید 'RSI'
    """
    df = df.copy()

    if 'Close' not in df.columns:
        raise ValueError("❌ Error: 'Close' column not found in DataFrame")

    close = pd.to_numeric(df['Close'], errors='coerce')
    df['Close'] = close
    df.dropna(subset=['Close'], inplace=True)

    if close.empty or close.isna().all():
        raise ValueError("❌ Error: 'Close' column is empty or full of NaNs after cleaning.")

    rsi = ta.momentum.RSIIndicator(close=close, window=window).rsi()
    df['RSI'] = rsi

    return df


def calculate_supertrend(df, period=10, multiplier=3):
    """
    محاسبه Supertrend و اضافه کردن آن به DataFrame
    پارامترها:
    - df: DataFrame ورودی با ستون‌های 'High', 'Low', 'Close'
    - period: طول دوره ATR (پیش‌فرض 10)
    - multiplier: ضریب ضرب ATR برای باندهای بالا و پایین (پیش‌فرض 3)
    
    خروجی:
    DataFrame با ستون جدید 'Supertrend' (bool)
    """
    df = df.copy()

    for col in ['High', 'Low', 'Close']:
        if col not in df.columns:
            raise ValueError(f"❌ Error: '{col}' column not found in DataFrame")

        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(subset=['High', 'Low', 'Close'], inplace=True)

    # اگر طول دیتافریم کمتر از period بود، ستون Supertrend بساز و مقدار True برگردون
    if len(df) < period:
        df['Supertrend'] = True
        return df

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