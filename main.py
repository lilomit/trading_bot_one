import matplotlib.pyplot as plt
from data import get_data
from strategies import supertrend_rsi_strategy, advanced_strategy
from backtest import run_backtest
from metrics import calculate_metrics

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
    plt.figure(figsize=(14, 6))
    plt.plot(df.index, df['Close'], label='Close Price', alpha=0.5)

    # سیگنال‌های خرید و فروش
    if 'Signal' in df.columns:
        plt.scatter(df.index[df['Signal']=='buy'], df['Close'][df['Signal']=='buy'], marker='^', color='green', label='Buy Signal')
        plt.scatter(df.index[df['Signal']=='sell'], df['Close'][df['Signal']=='sell'], marker='v', color='red', label='Sell Signal')

    # نمایش اندیکاتور Supertrend اگر داخل دیتافریم باشه
    if 'Supertrend' in df.columns:
        plt.plot(df.index, df['Supertrend'], label='Supertrend', color='orange')

    plt.title(name)
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_equity_curve(capital_over_time):
    plt.figure(figsize=(12, 4))
    plt.plot(capital_over_time, label='Equity Curve', color='blue')
    plt.title("📈 Equity Curve (Growth of Capital)")
    plt.xlabel("Time")
    plt.ylabel("Capital")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    df = get_data("BTC-USD", interval="5m", period="20d")

    if df is None or df.empty or len(df) < 20:
        print("⚠️ Data not available or too short. Check your connection or parameters.")
        return

    try:
        strategy_choice = input("Choose strategy (1: Supertrend+RSI, 2: Advanced): ").strip()
    except EOFError:
        strategy_choice = '1'

    if strategy_choice == '2':
        strategy_func = advanced_strategy
        strategy_name = "Advanced Strategy"
    else:
        strategy_func = supertrend_rsi_strategy
        strategy_name = "Supertrend + RSI"

    print(f"==== Running strategy: {strategy_name} ====")
    df_copy = df.copy()

    try:
        df_copy = strategy_func(df_copy)
    except Exception as e:
        print(f"❌ Error in strategy execution: {e}")
        return

    print(df_copy['Signal'].value_counts())

    final_capital, trade_log, capital_over_time = run_backtest(df_copy)
    metrics = calculate_metrics(capital_over_time, trade_log)
    metrics["Final Capital"] = final_capital

    print_trade_log(trade_log, name=strategy_name)
    print_metrics(metrics, name=strategy_name)
    plot_price_chart_with_indicators(df_copy, name=strategy_name)
    plot_equity_curve(capital_over_time)

if __name__ == "__main__":
    main()
