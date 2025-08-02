import pandas as pd

def run_backtest(df, initial_capital=1000.0, stop_loss_pct=None, take_profit_pct=None):
    capital = initial_capital
    position = 0.0
    entry_price = 0.0
    entry_time = None
    stop_loss_price = None
    take_profit_price = None
    trade_log = []
    capital_over_time = []

    # تبدیل مطمئن ایندکس به datetime (اگر نیست)
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, errors='coerce')
        df = df.dropna(subset=["Close"])

    for i in range(len(df)):
        sig = df['Signal'].iloc[i]
        price = float(df['Close'].iloc[i])
        low = float(df['Low'].iloc[i])
        high = float(df['High'].iloc[i])
        current_time = df.index[i]

        if sig == 'buy' and position == 0.0:
            position = capital / price
            entry_price = price
            entry_time = current_time
            capital = 0.0

            if stop_loss_pct is not None:
                stop_loss_price = entry_price * (1 - stop_loss_pct)
            else:
                stop_loss_price = None

            if take_profit_pct is not None:
                take_profit_price = entry_price * (1 + take_profit_pct)
            else:
                take_profit_price = None

            trade_log.append({
                "entry_time": entry_time.isoformat(),
                "exit_time": None,
                "entry_price": entry_price,
                "exit_price": None,
                "volume": position,
                "profit_pct": None,
                "reason": "buy"
            })

        elif position > 0.0:
            stop_hit = stop_loss_price is not None and low <= stop_loss_price
            take_hit = take_profit_price is not None and high >= take_profit_price
            close_signal = sig == 'sell'

            if stop_hit or take_hit or close_signal:
                if stop_hit:
                    exit_price = stop_loss_price
                    reason = "Stop Loss"
                elif take_hit:
                    exit_price = take_profit_price
                    reason = "Take Profit"
                else:
                    exit_price = price
                    reason = "Signal Sell"

                capital = position * exit_price
                profit_pct = (exit_price - entry_price) / entry_price * 100

                for trade in reversed(trade_log):
                    if trade["exit_time"] is None:
                        trade["exit_time"] = current_time.isoformat()
                        trade["exit_price"] = exit_price
                        trade["profit_pct"] = profit_pct
                        trade["reason"] = reason
                        break

                position = 0.0
                entry_price = 0.0
                entry_time = None
                stop_loss_price = None
                take_profit_price = None

        current_capital = capital + (position * price if position > 0.0 else 0.0)
        capital_over_time.append((df.index[i], current_capital))

    # فروش نهایی اگر موقعیت باز بود
    if position > 0.0:
        last_price = float(df['Close'].iloc[-1])
        capital = position * last_price
        profit_pct = (last_price - entry_price) / entry_price * 100
        current_time = df.index[-1].isoformat()

        for trade in reversed(trade_log):
            if trade["exit_time"] is None:
                trade["exit_time"] = current_time
                trade["exit_price"] = last_price
                trade["profit_pct"] = profit_pct
                trade["reason"] = "Final Sell"
                break

    return capital, trade_log, capital_over_time