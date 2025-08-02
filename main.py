import matplotlib.pyplot as plt
import pandas as pd
import os
import json
import matplotlib.dates as mdates

from data import get_data, resample_data
from strategies import supertrend_rsi_strategy, advanced_strategy
from backtest import run_backtest
from metrics import calculate_metrics
from config import SYMBOL, INTERVAL, PERIOD, INITIAL_CAPITAL, STOP_LOSS_PCT, TAKE_PROFIT_PCT, SUPERTREND_PERIOD, SUPERTREND_MULTIPLIER, ADV_SUPERTREND_PERIOD, ADV_SUPERTREND_MULTIPLIER
from database import init_db
from param_tuner import param_tuner


def print_trade_log(trade_log, name="Strategy"):
    print(f"\n📋 Trade Log ({name}):")
    if not trade_log:
        print("No trades executed.\n")
        return
    for log in trade_log:
        if isinstance(log, dict):
            etime = log.get("entry_time") or "-"
            xtime = log.get("exit_time") or "-"
            ep = log.get("entry_price") or "-"
            xp = log.get("exit_price") or "-"
            vol = log.get("volume") or "-"
            prof = log.get("profit_pct")
            prof_str = f"{prof:.2f}%" if prof is not None else "-"
            reason = log.get("reason") or "-"
            print(f"Entry: {etime} @ {ep:,.2f} | Exit: {xtime} @ {xp:,.2f} | Volume: {vol} | Profit: {prof_str} | Reason: {reason}")
        else:
            print(log)
    print()


def print_metrics(metrics, name="Strategy"):
    print(f"\n💰 Final Capital ({name}): {metrics.get('Final Capital', 0):,.2f} USD")
    print(f"\n📊 Backtest Metrics ({name}):")
    for key, value in metrics.items():
        if key != "Final Capital":
            # اگر مقدار عددی است فرمت کن، در غیر اینصورت مستقیم چاپ کن
            if isinstance(value, (int, float)):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
    print("\n" + "=" * 50 + "\n")


def plot_price_chart_with_indicators(df, name="Price & Indicators"):
    df = df.copy()
    if 'Close' not in df.columns:
        print("⚠️ Warning: 'Close' column not found in dataframe. Cannot plot price chart.")
        return

    df = df.dropna(subset=["Close"])
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
    if not capital_over_time:
        print("⚠️ No capital data to plot equity curve.")
        return
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


def save_results(strategy_name, trade_log, metrics, capital_over_time):
    os.makedirs("results", exist_ok=True)

    safe_name = strategy_name.replace(' ', '_')

    # ذخیره trade log به CSV
    if len(trade_log) > 0 and isinstance(trade_log[0], dict):
        pd.DataFrame(trade_log).to_csv(f"results/trade_log_{safe_name}.csv", index=False)
    else:
        pd.DataFrame({'Log': trade_log}).to_csv(f"results/trade_log_{safe_name}.csv", index=False)

    # ذخیره metrics به JSON
    with open(f"results/metrics_{safe_name}.json", "w") as f:
        json.dump(metrics, f, indent=4)

    # ذخیره equity curve به CSV
    capital_df = pd.DataFrame(capital_over_time, columns=['Time', 'Capital'])
    capital_df.to_csv(f"results/equity_curve_{safe_name}.csv", index=False)

    print(f"✅ Results saved to 'results/' folder.")


def convert_interval_to_minutes(interval):
    """تبدیل رشته تایم‌فریم به دقیقه برای متریک‌ها"""
    if interval.endswith('T'):
        return int(interval[:-1])
    elif interval == '1H':
        return 60
    elif interval == '1D':
        return 1440
    else:
        return 60  # مقدار پیش‌فرض


def main():
    print("\n" + "="*50)
    print("Initializing database...")
    init_db()
    print("Database initialized.")
    print("="*50 + "\n")

    df_original = get_data(SYMBOL, interval=INTERVAL, period=PERIOD)

    if df_original is None or df_original.empty or len(df_original) < 20:
        print("⚠️ Data not available or too short. Check your connection or parameters.")
        return

    print("Choose mode:")
    print("1: Run a single strategy")
    print("2: Parameter tuning (Grid Search) for Supertrend + RSI")
    try:
        mode = input("Enter mode (1 or 2): ").strip()
    except EOFError:
        mode = '1'

    if mode == '2':
        print("\nStarting parameter tuning...\n")
        param_grid = {
            "rsi_period": [7, 14],
            "rsi_buy_threshold": [25, 30],
            "rsi_sell_threshold": [65, 70],
            "supertrend_period": [7, 10],
            "supertrend_multiplier": [2, 3]
        }

        best, all_results = param_tuner(
            df_original,
            supertrend_rsi_strategy,
            param_grid,
            initial_capital=INITIAL_CAPITAL,
            stop_loss_pct=STOP_LOSS_PCT,
            take_profit_pct=TAKE_PROFIT_PCT,
            timeframe_minutes=convert_interval_to_minutes(INTERVAL)
        )

        if best:
            print("\n=== Best Parameter Set ===")
            print(best["params"])
            print("\nMetrics:")
            print_metrics(best["metrics"], name="Best Params")

        return

    try:
        strategy_choice = input("Choose strategy (1: Supertrend+RSI, 2: Advanced): ").strip()
    except EOFError:
        strategy_choice = '1'

    if strategy_choice == '2':
        strategy_func = lambda df: advanced_strategy(
            df,
            rsi_window=7,
            supertrend_period=ADV_SUPERTREND_PERIOD,
            supertrend_multiplier=ADV_SUPERTREND_MULTIPLIER
        )
        strategy_name = "Advanced Strategy"
    else:
        strategy_func = lambda df: supertrend_rsi_strategy(
            df,
            rsi_period=14,
            rsi_buy_threshold=30,
            rsi_sell_threshold=70,
            supertrend_period=SUPERTREND_PERIOD,
            supertrend_multiplier=SUPERTREND_MULTIPLIER
        )
        strategy_name = "Supertrend + RSI"

    # لیست تایم‌فریم‌های مورد نظر برای بک‌تست
    timeframes = ['5T', '15T', '1H', '1D']

    for tf in timeframes:
        print("\n" + "="*50)
        print(f"Starting backtest for timeframe: {tf}")
        print("="*50 + "\n")

        # اگر تایم‌فریم داده برابر با تایم‌فریم اصلی بود نیازی به resample نیست
        if tf == INTERVAL:
            df_tf = df_original.copy()
        else:
            df_tf = resample_data(df_original, tf)

        try:
            df_tf = strategy_func(df_tf)
        except Exception as e:
            print(f"❌ Error in strategy execution for timeframe {tf}: {e}")
            continue

        # نمایش تعداد سیگنال‌ها
        if 'Signal' in df_tf.columns:
            buy_signals = (df_tf['Signal'] == 'buy').sum()
            sell_signals = (df_tf['Signal'] == 'sell').sum()
            print(f"Signals generated — Buy: {buy_signals:,}, Sell: {sell_signals:,}\n")
        else:
            print("⚠️ No 'Signal' column found in data after strategy application.\n")

        final_capital, trade_log, capital_over_time = run_backtest(
            df_tf,
            initial_capital=INITIAL_CAPITAL,
            stop_loss_pct=STOP_LOSS_PCT,
            take_profit_pct=TAKE_PROFIT_PCT
        )

        metrics = calculate_metrics(
            capital_over_time,
            trade_log,
            initial_capital=INITIAL_CAPITAL,
            timeframe_minutes=convert_interval_to_minutes(tf)
        )
        metrics["Final Capital"] = final_capital

        print_trade_log(trade_log, name=f"{strategy_name} {tf}")
        print_metrics(metrics, name=f"{strategy_name} {tf}")
        save_results(f"{strategy_name}_{tf}", trade_log, metrics, capital_over_time)

        # نمایش اجباری نمودارها با کنترل خطا
        try:
            plot_price_chart_with_indicators(df_tf, name=f"{strategy_name} {tf}")
            plot_equity_curve(capital_over_time)
        except Exception as e:
            print(f"⚠️ Error showing plots for timeframe {tf}: {e}")

        print("\n" + "="*50 + "\n")

    print("All backtests completed.")


if __name__ == "__main__":
    main()