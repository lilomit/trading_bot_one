import pandas as pd
from datetime import datetime

from data import get_data
from config import (
    SYMBOL, INTERVAL, PERIOD, INITIAL_CAPITAL,
    STOP_LOSS_PCT, TAKE_PROFIT_PCT, TRADING_FEE_PCT,
    SUPERTREND_PERIOD, SUPERTREND_MULTIPLIER,
    ADV_SUPERTREND_PERIOD, ADV_SUPERTREND_MULTIPLIER
)

from strategies.supertrend_rsi_strategy import supertrend_rsi_strategy
from strategies.advanced_strategy import advanced_strategy

from backtest import run_backtest
from metrics import calculate_metrics
from utils.time import convert_interval_to_minutes
from utils.file import create_output_folder, get_filepath

# تعریف استراتژی‌ها به صورت لیست
STRATEGIES = [
    {
        "name": "Supertrend + RSI",
        "func": lambda df: supertrend_rsi_strategy(
            df,
            rsi_period=14,
            rsi_buy_threshold=30,
            rsi_sell_threshold=70,
            supertrend_period=SUPERTREND_PERIOD,
            supertrend_multiplier=SUPERTREND_MULTIPLIER
        )
    },
    {
        "name": "Advanced Strategy",
        "func": lambda df: advanced_strategy(
            df,
            rsi_window=7,
            supertrend_period=ADV_SUPERTREND_PERIOD,
            supertrend_multiplier=ADV_SUPERTREND_MULTIPLIER
        )
    }
]

def compare_strategies():
    df = get_data(SYMBOL, interval=INTERVAL, period=PERIOD)
    if df is None or df.empty:
        print("⚠️ No data found.")
        return

    results = []

    for strat in STRATEGIES:
        try:
            df_strategy = strat["func"](df.copy())

            final_capital, trade_log, capital_over_time, _ = run_backtest(
                df_strategy,
                initial_capital=INITIAL_CAPITAL,
                stop_loss_pct=STOP_LOSS_PCT,
                take_profit_pct=TAKE_PROFIT_PCT,
                trading_fee_pct=TRADING_FEE_PCT
            )

            metrics = calculate_metrics(
                capital_over_time,
                trade_log,
                initial_capital=INITIAL_CAPITAL,
                timeframe_minutes=convert_interval_to_minutes(INTERVAL)
            )
            metrics["Final Capital"] = final_capital
            metrics["Strategy"] = strat["name"]

            results.append(metrics)

        except Exception as e:
            print(f"❌ Error running strategy {strat['name']}: {e}")

    if not results:
        print("⚠️ No results to compare.")
        return

    df_results = pd.DataFrame(results)
    df_results = df_results[["Strategy", "Final Capital", "Total Return (%)", "Sharpe Ratio", "Win Rate (%)"]]

    print("\n📊 Strategy Comparison:\n")
    print(df_results)

    # ساخت پوشه خروجی و ذخیره فایل
    output_dir = create_output_folder(strategy_name="strategy_comparison")
    csv_path = get_filepath(output_dir, "strategy_comparison.csv")
    df_results.to_csv(csv_path, index=False)
    print(f"\n💾 Results saved to: {csv_path}")

if __name__ == "__main__":
    compare_strategies()