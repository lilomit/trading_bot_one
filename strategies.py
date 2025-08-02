import pandas as pd
from indicators import calculate_rsi, calculate_supertrend

def supertrend_rsi_strategy(df, rsi_period=14, rsi_buy_threshold=30, rsi_sell_threshold=70, supertrend_period=10, supertrend_multiplier=3):
    df = df.copy()

    # محاسبه اندیکاتورها
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


def advanced_strategy(df, rsi_window=7, supertrend_period=7, supertrend_multiplier=2):
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