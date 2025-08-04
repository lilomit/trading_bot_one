import pandas as pd
from indicators import calculate_rsi, calculate_supertrend

def supertrend_rsi_strategy(
    df,
    rsi_period=14,
    rsi_buy_threshold=30,
    rsi_sell_threshold=70,
    supertrend_period=10,
    supertrend_multiplier=3
):
    """
    استراتژی ترکیبی Supertrend و RSI

    پارامترها:
    - df: DataFrame ورودی با داده‌های OHLCV
    - rsi_period: دوره RSI (پیش‌فرض 14)
    - rsi_buy_threshold: حد آستانه خرید RSI (پیش‌فرض 30)
    - rsi_sell_threshold: حد آستانه فروش RSI (پیش‌فرض 70)
    - supertrend_period: دوره Supertrend (پیش‌فرض 10)
    - supertrend_multiplier: ضریب Supertrend (پیش‌فرض 3)

    خروجی:
    DataFrame با ستون جدید 'Signal' که مقادیر 'buy', 'sell' یا 'hold' دارد
    """
    df = df.copy()

    df = calculate_rsi(df, window=rsi_period)
    df = calculate_supertrend(df, period=supertrend_period, multiplier=supertrend_multiplier)

    df['Signal'] = 'hold'
    position_open = False

    for i in range(1, len(df)):
        rsi = df['RSI'].iloc[i]
        supertrend = df['Supertrend'].iloc[i]
        if pd.isna(rsi) or pd.isna(supertrend):
            continue

        if not position_open and rsi < rsi_buy_threshold and supertrend:
            df.at[df.index[i], 'Signal'] = 'buy'
            position_open = True
        elif position_open and (rsi > rsi_sell_threshold or not supertrend):
            df.at[df.index[i], 'Signal'] = 'sell'
            position_open = False

    return df