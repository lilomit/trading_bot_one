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
            "Sortino Ratio", "Calmar Ratio", "Expectancy", "Std Dev of Returns",
            "Avg Win / Avg Loss", "Max Consecutive Wins", "Max Consecutive Losses",
            "Win Rate (%)", "Profit Factor", "Average Trade Return (%)"
        ]}

    # 📈 Total Return
    final_capital = df['Capital'].iloc[-1]
    total_return = (final_capital / initial_capital - 1) * 100

    # 🕒 Annualized Return
    days = (df.index[-1] - df.index[0]).total_seconds() / (3600 * 24)
    years = days / 365.25

    annualized_return = 0
    if years > 0:
        with np.errstate(over='ignore'):
            val = (final_capital / initial_capital) ** (1 / years) - 1
            if np.isfinite(val):
                annualized_return = val * 100
            else:
                annualized_return = float('inf')

    # 📉 Max Drawdown
    roll_max = df['Capital'].cummax()
    drawdown = (df['Capital'] - roll_max) / roll_max
    max_drawdown = drawdown.min() * 100

    # 📊 Sharpe Ratio
    returns = df['Capital'].pct_change().dropna()
    periods_per_year = (60 / timeframe_minutes) * 24 * 252  # 252 روز معاملاتی در سال
    sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(periods_per_year) if returns.std() != 0 else 0

    # Sortino Ratio (فقط از بازده‌های منفی برای محاسبه واریانس استفاده می‌کنیم)
    negative_returns = returns[returns < 0]
    downside_std = negative_returns.std()
    sortino_ratio = (returns.mean() / downside_std) * np.sqrt(periods_per_year) if downside_std != 0 else 0

    # Calmar Ratio = Annualized Return / -Max Drawdown (اگر Max Drawdown صفر یا مثبت باشه 0)
    calmar_ratio = annualized_return / (-max_drawdown) if max_drawdown < 0 else 0

    # Std Deviation of Returns
    std_dev_returns = returns.std()

    # محاسبه Expectancy = (Avg Win * Win Rate) - (Avg Loss * Loss Rate)
    wins, losses = 0, 0
    gross_profit = 0
    gross_loss = 0
    profit_sum = 0
    trade_count = 0

    consecutive_wins = 0
    max_consecutive_wins = 0
    consecutive_losses = 0
    max_consecutive_losses = 0

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
            consecutive_wins += 1
            consecutive_losses = 0
            if consecutive_wins > max_consecutive_wins:
                max_consecutive_wins = consecutive_wins
        else:
            losses += 1
            gross_loss += abs(profit_pct)
            consecutive_losses += 1
            consecutive_wins = 0
            if consecutive_losses > max_consecutive_losses:
                max_consecutive_losses = consecutive_losses

    win_rate = (wins / trade_count) if trade_count > 0 else 0
    loss_rate = 1 - win_rate

    avg_win = (gross_profit / wins) if wins > 0 else 0
    avg_loss = (gross_loss / losses) if losses > 0 else 0

    expectancy = (avg_win * win_rate) - (avg_loss * loss_rate)

    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')
    avg_trade_return = (profit_sum / trade_count) if trade_count > 0 else 0

    return {
        "Total Return (%)": total_return,
        "Annualized Return (%)": annualized_return,
        "Max Drawdown (%)": max_drawdown,
        "Sharpe Ratio": sharpe_ratio,
        "Sortino Ratio": sortino_ratio,
        "Calmar Ratio": calmar_ratio,
        "Expectancy": expectancy,
        "Std Dev of Returns": std_dev_returns,
        "Avg Win / Avg Loss": (avg_win / avg_loss) if avg_loss != 0 else float('inf'),
        "Max Consecutive Wins": max_consecutive_wins,
        "Max Consecutive Losses": max_consecutive_losses,
        "Win Rate (%)": win_rate * 100,
        "Profit Factor": profit_factor,
        "Average Trade Return (%)": avg_trade_return,
    }