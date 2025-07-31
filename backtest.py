# backtest.py

def run_backtest(df, initial_capital=1000.0):
    capital = initial_capital
    position = 0.0        # واحد BTC در پوزیشن
    entry_price = 0.0     # قیمت ورود آخرین پوزیشن
    trade_log = []
    capital_over_time = []

    for i in range(len(df)):
        sig   = df['Signal'].iloc[i]
        price = float(df['Close'].iloc[i])  # تبدیل امن به float

        # دستور خرید
        if sig == 'buy' and position == 0.0:
            position = capital / price
            entry_price = price
            capital = 0.0
            trade_log.append(f"🟢 BUY  at {price:.2f} | Time: {df.index[i]}")
        
        # دستور فروش
        elif sig == 'sell' and position > 0.0:
            capital = position * price
            profit_pct = (price - entry_price) / entry_price * 100
            trade_log.append(
                f"🔴 SELL at {price:.2f} | Time: {df.index[i]} | Profit: {profit_pct:.2f}% | Capital: {capital:.2f}"
            )
            position = 0.0
            entry_price = 0.0

        # ثبت سرمایه در هر قدم
        current_capital = capital + (position * price if position > 0.0 else 0.0)
        capital_over_time.append((df.index[i], current_capital))

    # بستن پوزیشن باز در پایان داده‌ها
    if position > 0.0:
        last_price = float(df['Close'].iloc[-1])
        capital = position * last_price
        profit_pct = (last_price - entry_price) / entry_price * 100
        trade_log.append(
            f"🔁 Final SELL at {last_price:.2f} | Profit: {profit_pct:.2f}% | Capital: {capital:.2f}"
        )
        position = 0.0

    return capital, trade_log, capital_over_time
