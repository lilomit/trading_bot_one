import numpy as np
import pandas as pd

def calculate_metrics(capital_over_time, trade_log, initial_capital=1000, timeframe_minutes=5):
    df = pd.DataFrame(capital_over_time, columns=['Time', 'Capital'])
    df['Time'] = pd.to_datetime(df['Time'])
    df.set_index('Time', inplace=True)
    df = df.sort_index()

    if df.empty:
        return {k: 0 for k in [
            "Total Return (%)", "Annualized Return (%)", "Max Drawdown (%)", "Sharpe Ratio",
            "Win Rate (%)", "Profit Factor", "Average Trade Return (%)"
        ]}

    # 📈 Total Return
    final_capital = df['Capital'].iloc[-1]
    total_return = (final_capital / initial_capital - 1) * 100

    # 🕒 Annualized Return
    days = (df.index[-1] - df.index[0]).total_seconds() / (3600 * 24)
    years = days / 365.25
    annualized_return = ((final_capital / initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0

    # 📉 Max Drawdown
    roll_max = df['Capital'].cummax()
    drawdown = (df['Capital'] - roll_max) / roll_max
    max_drawdown = drawdown.min() * 100

    # 📊 Sharpe Ratio
    returns = df['Capital'].pct_change().dropna()
    periods_per_year = (60 / timeframe_minutes) * 24 * 252  # 252 روز معاملاتی در سال
    sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(periods_per_year) if returns.std() != 0 else 0

    # 📌 تحلیل trade_log برای Win Rate و Profit Factor و Avg Trade Return
    wins, losses = 0, 0
    profit_sum = 0
    gross_profit = 0
    gross_loss = 0
    trade_count = 0

    for trade in trade_log:
        if not isinstance(trade, dict):
            continue
        profit_pct = trade.get('profit_pct')
        if profit_pct is None:
            continue

        trade_count += 1
        profit_sum += profit_pct
        if profit_pct > 0:
            wins += 1
            gross_profit += profit_pct
        else:
            losses += 1
            gross_loss += abs(profit_pct)

    win_rate = (wins / trade_count) * 100 if trade_count > 0 else 0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')
    avg_trade_return = (profit_sum / trade_count) if trade_count > 0 else 0

    return {
        "Total Return (%)": total_return,
        "Annualized Return (%)": annualized_return,
        "Max Drawdown (%)": max_drawdown,
        "Sharpe Ratio": sharpe_ratio,
        "Win Rate (%)": win_rate,
        "Profit Factor": profit_factor,
        "Average Trade Return (%)": avg_trade_return,
    }