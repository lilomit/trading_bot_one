import pandas as pd


def enter_trade(capital, price, trading_fee_pct, stop_loss_pct, take_profit_pct, current_time):
    fee_cost = capital * trading_fee_pct
    net_capital = capital - fee_cost
    position = net_capital / price
    entry_price = price
    entry_time = current_time
    stop_loss_price = entry_price * (1 - stop_loss_pct) if stop_loss_pct else None
    take_profit_price = entry_price * (1 + take_profit_pct) if take_profit_pct else None

    trade = {
        "entry_time": entry_time.isoformat(),
        "exit_time": None,
        "entry_price": entry_price,
        "exit_price": None,
        "volume": position,
        "profit_pct": None,
        "reason": "buy",
        "fee_cost_entry": fee_cost
    }
    return position, entry_price, entry_time, stop_loss_price, take_profit_price, net_capital, fee_cost, trade


def exit_trade(position, entry_price, price, trading_fee_pct, current_time, trade_log, reason):
    gross_capital = position * price
    fee_cost = gross_capital * trading_fee_pct
    net_capital = gross_capital - fee_cost
    profit_pct = (net_capital - (position * entry_price)) / (position * entry_price) * 100

    # Update the last open trade
    for trade in reversed(trade_log):
        if trade["exit_time"] is None:
            trade.update({
                "exit_time": current_time.isoformat() if hasattr(current_time, "isoformat") else str(current_time),
                "exit_price": price,
                "profit_pct": profit_pct,
                "reason": reason,
                "fee_cost_exit": fee_cost
            })
            break

    return net_capital, fee_cost


def run_backtest(
    df,
    initial_capital=1000.0,
    stop_loss_pct=None,
    take_profit_pct=None,
    trading_fee_pct=0.0
):
    capital = initial_capital
    position = 0.0
    entry_price = 0.0
    entry_time = None
    stop_loss_price = None
    take_profit_price = None
    trade_log = []
    capital_over_time = []
    total_fees = 0.0

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
            (
                position,
                entry_price,
                entry_time,
                stop_loss_price,
                take_profit_price,
                capital,
                fee_cost,
                trade
            ) = enter_trade(capital, price, trading_fee_pct, stop_loss_pct, take_profit_pct, current_time)

            total_fees += fee_cost
            trade_log.append(trade)

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

                net_capital, fee_cost = exit_trade(
                    position, entry_price, exit_price, trading_fee_pct, current_time, trade_log, reason
                )

                total_fees += fee_cost
                capital = net_capital

                position = 0.0
                entry_price = 0.0
                entry_time = None
                stop_loss_price = None
                take_profit_price = None

        current_cap = capital + (position * price if position > 0.0 else 0.0)
        capital_over_time.append((current_time, current_cap))

    # Final close if position still open
    if position > 0.0:
        last_price = float(df['Close'].iloc[-1])
        net_capital, fee_cost = exit_trade(
            position, entry_price, last_price, trading_fee_pct, df.index[-1], trade_log, "Final Sell"
        )
        total_fees += fee_cost
        capital = net_capital

    return capital, trade_log, capital_over_time, total_fees