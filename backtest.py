import pandas as pd

def run_backtest(df, initial_capital=1000.0):
    capital = initial_capital
    position = 0.0
    entry_price = 0.0
    trade_log = []
    capital_over_time = []

    # تبدیل مطمئن ایندکس به datetime (اگر نیست)
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, errors='coerce')
        df = df.dropna(subset=["Close"])  # حذف ردیف‌های مشکل‌دار (اگر ایندکس None شد)

    for i in range(len(df)):
        sig = df['Signal'].iloc[i]
        price = float(df['Close'].iloc[i])

        if sig == 'buy' and position == 0.0:
            position = capital / price
            entry_price = price
            capital = 0.0
            trade_log.append(f"🟢 BUY  at {price:.2f} | Time: {df.index[i]}")

        elif sig == 'sell' and position > 0.0:
            capital = position * price
            profit_pct = (price - entry_price) / entry_price * 100
            trade_log.append(
                f"🔴 SELL at {price:.2f} | Time: {df.index[i]} | Profit: {profit_pct:.2f}% | Capital: {capital:.2f}"
            )
            position = 0.0
            entry_price = 0.0

        current_capital = capital + (position * price if position > 0.0 else 0.0)
        capital_over_time.append((df.index[i], current_capital))

    if position > 0.0:
        last_price = float(df['Close'].iloc[-1])
        capital = position * last_price
        profit_pct = (last_price - entry_price) / entry_price * 100
        trade_log.append(
            f"🔁 Final SELL at {last_price:.2f} | Profit: {profit_pct:.2f}% | Capital: {capital:.2f}"
        )

    return capital, trade_log, capital_over_time