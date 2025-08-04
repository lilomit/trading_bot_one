import pandas as pd
from indicators import calculate_rsi, calculate_supertrend

def advanced_strategy(
    df,
    rsi_window=7,
    supertrend_period=7,
    supertrend_multiplier=2
):
    """
    استراتژی پیشرفته با ترکیب RSI و Supertrend

    پارامترها:
    - df: DataFrame ورودی
    - rsi_window: طول دوره RSI (پیش‌فرض 7)
    - supertrend_period: دوره Supertrend (پیش‌فرض 7)
    - supertrend_multiplier: ضریب Supertrend (پیش‌فرض 2)

    خروجی:
    DataFrame با ستون 'Signal' شامل مقادیر 'buy', 'sell', یا 'hold'
    """
    df = df.copy()
    df = calculate_rsi(df, window=rsi_window)
    df = calculate_supertrend(df, period=supertrend_period, multiplier=supertrend_multiplier)

    if len(df) == 0 or 'RSI' not in df.columns or 'Supertrend' not in df.columns:
        df['Signal'] = 'hold'
        return df

    df['Signal'] = 'hold'

    for i in range(1, len(df)):
        if df['RSI'].iloc[i] < 40 and df['Supertrend'].iloc[i]:
            df.at[df.index[i], 'Signal'] = 'buy'
        elif df['RSI'].iloc[i] > 75 and not df['Supertrend'].iloc[i]:
            df.at[df.index[i], 'Signal'] = 'sell'

    return df