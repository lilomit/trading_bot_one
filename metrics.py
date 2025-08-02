import numpy as np
import pandas as pd

def calculate_metrics(capital_over_time, trade_log, initial_capital=1000, timeframe_minutes=5):
    df = pd.DataFrame(capital_over_time, columns=['Time', 'Capital'])

    df['Time'] = pd.to_datetime(df['Time'])
    df.set_index('Time', inplace=True)
    df = df.sort_index()

    if len(df) == 0:
        return {k: 0 for k in [
            "Total Return (%)", "Annualized Return (%)", "Max Drawdown (%)", "Sharpe Ratio",
            "Win Rate (%)", "Profit Factor", "Average Trade Return (%)"
        ]}

    total_return = (df['Capital'].iloc[-1] / initial_capital - 1) * 100

    days = (df.index[-1] - df.index[0]).total_seconds() / (3600 * 24)
    years = days / 365.25
    annualized_return = ((df['Capital'].iloc[-1] / initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0

    roll_max = df['Capital'].cummax()
    drawdown = (df['Capital'] - roll_max) / roll_max
    max_drawdown = drawdown.min() * 100

    returns = df['Capital'].pct_change().dropna()
    periods_per_year = (60 / timeframe_minutes) * 24 * 252
    sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(periods_per_year) if returns.std() != 0 else 0

    wins, losses = 0, 0
    gross_profit, gross_loss = 0, 0

    for log in trade_log:
        if 'Profit:' in log:
            profit_str = log.split('Profit: ')[1].split('%')[0]
            profit = float(profit_str)
            if profit > 0:
                wins += 1
                gross_profit += profit
            else:
                losses += 1
                gross_loss += abs(profit)

    total_trades = wins + losses
    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    avg_trade_return = (gross_profit - gross_loss) / total_trades if total_trades > 0 else 0

    return {
        "Total Return (%)": total_return,
        "Annualized Return (%)": annualized_return,
        "Max Drawdown (%)": max_drawdown,
        "Sharpe Ratio": sharpe_ratio,
        "Win Rate (%)": win_rate,
        "Profit Factor": profit_factor,
        "Average Trade Return (%)": avg_trade_return,
    }