from indicators import calculate_rsi, calculate_supertrend

def supertrend_rsi_strategy(df, rsi_period=14, rsi_threshold=50, supertrend_period=10, supertrend_multiplier=3):
    df = df.copy()  # جلوگیری از تغییر دیتافریم اصلی
    df = calculate_rsi(df, window=rsi_period)
    df = calculate_supertrend(df, period=supertrend_period, multiplier=supertrend_multiplier)

    df['Signal'] = 'hold'

    for i in range(1, len(df)):
        if df['RSI'].iloc[i] < rsi_threshold and df['Supertrend'].iloc[i]:
            df.at[df.index[i], 'Signal'] = 'buy'
        elif df['RSI'].iloc[i] > 70 and not df['Supertrend'].iloc[i]:
            df.at[df.index[i], 'Signal'] = 'sell'

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