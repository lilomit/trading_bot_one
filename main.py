import matplotlib.pyplot as plt
import pandas as pd
from data import get_data
from strategies import supertrend_rsi_strategy, advanced_strategy
from backtest import run_backtest
from metrics import calculate_metrics
from config import SYMBOL, INTERVAL, PERIOD, INITIAL_CAPITAL
import matplotlib.dates as mdates

def print_trade_log(trade_log, name="Strategy"):
    print(f"📋 Trade Log ({name}):")
    for log in trade_log:
        print(log)
    print()

def print_metrics(metrics, name="Strategy"):
    print(f"\n💰 Final Capital ({name}): {metrics['Final Capital']:.2f} USD")
    print(f"\n📊 Backtest Metrics ({name}):")
    for key, value in metrics.items():
        if key != "Final Capital":
            print(f"{key}: {value:.2f}")
    print("\n" + "=" * 30 + "\n")

def plot_price_chart_with_indicators(df, name="Price & Indicators"):
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    df = df.copy()
    if 'Close' not in df.columns:
        print("⚠️ Warning: 'Close' column not found in dataframe. Cannot plot price chart.")
        return

    df = df.dropna(subset=["Close"])  # اطمینان از نبود NaN
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, errors='coerce')
        df = df.dropna(subset=["Close"])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

    ax1.plot(df.index, df['Close'], label='Close Price', color='gray', alpha=0.6)

    if 'Signal' in df.columns:
        ax1.scatter(df.index[df['Signal']=='buy'], df['Close'][df['Signal']=='buy'], marker='^', color='green', label='Buy Signal')
        ax1.scatter(df.index[df['Signal']=='sell'], df['Close'][df['Signal']=='sell'], marker='v', color='red', label='Sell Signal')

    if 'Supertrend' in df.columns and df['Supertrend'].dtype != 'bool':
        ax1.plot(df.index, df['Supertrend'], label='Supertrend', color='orange')

    ax1.set_ylabel("Price")
    ax1.legend()
    ax1.grid(True)
    ax1.set_title(name)

    if 'RSI' in df.columns:
        ax2.plot(df.index, df['RSI'], label='RSI', color='purple')
        ax2.axhline(70, color='red', linestyle='--', linewidth=1, label='Overbought (70)')
        ax2.axhline(30, color='green', linestyle='--', linewidth=1, label='Oversold (30)')
        ax2.set_ylabel("RSI")
        ax2.set_ylim(0, 100)
        ax2.legend()
        ax2.grid(True)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_equity_curve(capital_over_time):
    times, capitals = zip(*capital_over_time)

    plt.figure(figsize=(16, 5))
    plt.plot(times, capitals, label='Equity Curve', color='blue', linewidth=2)
    plt.title("📈 Equity Curve (Growth of Capital)")
    plt.xlabel("Time")
    plt.ylabel("Capital")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.show()

def main():
    df = get_data(SYMBOL, interval=INTERVAL, period=PERIOD)

    if df is None or df.empty or len(df) < 20:
        print("⚠️ Data not available or too short. Check your connection or parameters.")
        return

    try:
        strategy_choice = input("Choose strategy (1: Supertrend+RSI, 2: Advanced): ").strip()
    except EOFError:
        strategy_choice = '1'

    if strategy_choice == '2':
        from config import ADV_SUPERTREND_PERIOD, ADV_SUPERTREND_MULTIPLIER
        strategy_func = lambda df: advanced_strategy(df, rsi_window=7, supertrend_period=ADV_SUPERTREND_PERIOD, supertrend_multiplier=ADV_SUPERTREND_MULTIPLIER)
        strategy_name = "Advanced Strategy"
    else:
        from config import SUPERTREND_PERIOD, SUPERTREND_MULTIPLIER
        strategy_func = lambda df: supertrend_rsi_strategy(df, supertrend_period=SUPERTREND_PERIOD, supertrend_multiplier=SUPERTREND_MULTIPLIER)
        strategy_name = "Supertrend + RSI"

    print(f"==== Running strategy: {strategy_name} ====")
    df_copy = df.copy()
    print("📦 DF Copy Columns:", df_copy.columns)
    print(df_copy.head())
    try:
        df_copy = strategy_func(df_copy)
    except Exception as e:
        print(f"❌ Error in strategy execution: {e}")
        return

    print(df_copy['Signal'].value_counts())

    final_capital, trade_log, capital_over_time = run_backtest(df_copy, initial_capital=INITIAL_CAPITAL)
    metrics = calculate_metrics(capital_over_time, trade_log, initial_capital=INITIAL_CAPITAL)
    metrics["Final Capital"] = final_capital

    print_trade_log(trade_log, name=strategy_name)
    print_metrics(metrics, name=strategy_name)
    print("📦 Available Columns in df_copy:", df_copy.columns.tolist())
    plot_price_chart_with_indicators(df_copy, name=strategy_name)
    plot_equity_curve(capital_over_time)

if __name__ == "__main__":
    main()