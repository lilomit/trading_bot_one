import pandas as pd
from indicators import calculate_rsi, calculate_supertrend

def supertrend_rsi_strategy(df, rsi_period=14, rsi_threshold=50, supertrend_period=10, supertrend_multiplier=3):
    df = calculate_rsi(df, window=rsi_period)
    df = calculate_supertrend(df, period=supertrend_period, multiplier=supertrend_multiplier)

    signals = ['hold']
    for i in range(1, len(df)):
        if df['RSI'].iloc[i] < rsi_threshold and df['Supertrend'].iloc[i]:
            signals.append('buy')
        elif df['RSI'].iloc[i] > 70 and not df['Supertrend'].iloc[i]:
            signals.append('sell')
        else:
            signals.append('hold')

    df = df.iloc[len(df) - len(signals):].copy()
    df['Signal'] = signals
    return df

def advanced_strategy(df):
    df = calculate_rsi(df, window=7)
    df = calculate_supertrend(df, period=7, multiplier=2)

    if len(df) == 0 or 'RSI' not in df.columns or 'Supertrend' not in df.columns:
        df['Signal'] = ['hold'] * len(df)
        return df

    signals = ['hold']
    for i in range(1, len(df)):
        if df['RSI'].iloc[i] < 40 and df['Supertrend'].iloc[i]:
            signals.append('buy')
        elif df['RSI'].iloc[i] > 75 and not df['Supertrend'].iloc[i]:
            signals.append('sell')
        else:
            signals.append('hold')

    df = df.iloc[len(df) - len(signals):].copy()
    df['Signal'] = signals
    return df
