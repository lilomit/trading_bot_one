import pandas as pd
import ta

def calculate_rsi(df, window=14):
    # استخراج Close به‌صورت Series مطمئن
    close = df['Close']
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close_series = pd.to_numeric(close, errors='coerce').dropna()

    # محاسبه RSI
    rsi = ta.momentum.RSIIndicator(close=close_series, window=window).rsi()
    # چون rsi ایندکس اصلی رو حفظ نمی‌کنه، مجدداً به df می‌چسبونیم
    df = df.loc[rsi.index]
    df['RSI'] = rsi
    return df

def calculate_supertrend(df, period=10, multiplier=3):
    # تبدیل ستون‌ها به Series عددی
    high = df['High']
    low = df['Low']
    close = df['Close']
    if isinstance(high, pd.DataFrame):
        high = high.iloc[:, 0]
        low = low.iloc[:, 0]
        close = close.iloc[:, 0]
    high = pd.to_numeric(high, errors='coerce')
    low = pd.to_numeric(low, errors='coerce')
    close = pd.to_numeric(close, errors='coerce')

    # حذف ردیف‌های ناقص
    temp = pd.concat([high, low, close], axis=1).dropna()
    high, low, close = temp.iloc[:,0], temp.iloc[:,1], temp.iloc[:,2]

    atr = ta.volatility.AverageTrueRange(high=high, low=low, close=close, window=period).average_true_range()
    hl2 = (high + low) / 2
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    supertrend = pd.Series(index=temp.index, dtype='bool')
    # مقدار اولیه بر اساس Close vs mid
    supertrend.iloc[0] = True
    for i in range(1, len(temp)):
        idx = temp.index[i]
        if close.iloc[i] > upperband.iloc[i - 1]:
            supertrend.iloc[i] = True
        elif close.iloc[i] < lowerband.iloc[i - 1]:
            supertrend.iloc[i] = False
        else:
            supertrend.iloc[i] = supertrend.iloc[i - 1]

    # الحاق به df اصلی
    df = df.loc[supertrend.index]
    df['Supertrend'] = supertrend.values
    return df
