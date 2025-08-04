import pandas as pd
import os

from data import get_data, resample_data
from strategies.supertrend_rsi_strategies import supertrend_rsi_strategy
from strategies.advanced_strategies import advanced_strategy
from backtest import run_backtest
from metrics import calculate_metrics
from database import init_db
from param_tuner import param_tuner
from walkforward import walk_forward_validation

from config import (
    SYMBOL, INTERVAL, PERIOD, INITIAL_CAPITAL,
    STOP_LOSS_PCT, TAKE_PROFIT_PCT,
    SUPERTREND_PERIOD, SUPERTREND_MULTIPLIER,
    ADV_SUPERTREND_PERIOD, ADV_SUPERTREND_MULTIPLIER,
    TRADING_FEE_PCT
)

from utils.time import convert_interval_to_minutes
from utils.report import print_trade_log, print_metrics, save_results
from utils.plot import plot_price_chart_with_indicators, plot_equity_curve
from utils.file import create_output_folder, get_filepath


def split_data_for_out_of_sample(df, split_ratio=0.8):
    if df is None or df.empty:
        return None, None
    split_index = int(len(df) * split_ratio)
    return df.iloc[:split_index].copy(), df.iloc[split_index:].copy()


def run_backtest_and_report(df, strategy_func, strategy_name, timeframe, suffix=""):
    if df is None or df.empty:
        print(f"⚠️ No data for {strategy_name} {timeframe} {suffix}")
        return

    min_required_length = max(SUPERTREND_PERIOD, 14, ADV_SUPERTREND_PERIOD)
    if len(df) < min_required_length:
        print(f"⚠️ Data too short for {strategy_name} {timeframe} {suffix}. Skipping.")
        return

    try:
        df = strategy_func(df)
    except Exception as e:
        print(f"❌ Error in strategy execution for {strategy_name} {timeframe} {suffix}: {e}")
        return

    if 'Signal' in df.columns:
        print(f"Signals — Buy: {(df['Signal'] == 'buy').sum()}, Sell: {(df['Signal'] == 'sell').sum()}")
    else:
        print("⚠️ No 'Signal' column found after applying strategy.")
        return

    final_capital, trade_log, capital_over_time, total_fees = run_backtest(
        df,
        initial_capital=INITIAL_CAPITAL,
        stop_loss_pct=STOP_LOSS_PCT,
        take_profit_pct=TAKE_PROFIT_PCT,
        trading_fee_pct=TRADING_FEE_PCT
    )

    metrics = calculate_metrics(
        capital_over_time,
        trade_log,
        initial_capital=INITIAL_CAPITAL,
        timeframe_minutes=convert_interval_to_minutes(timeframe)
    )
    metrics["Final Capital"] = final_capital

    print_trade_log(trade_log, name=f"{strategy_name} {timeframe} {suffix}")
    print_metrics(metrics, name=f"{strategy_name} {timeframe} {suffix}")
    print(f"💸 Total Trading Fees: {total_fees:.4f} USD\n")

    output_folder = create_output_folder(strategy_name=f"{strategy_name}_{timeframe}_{suffix}".strip('_'))

    save_results(
        strategy_name=f"{strategy_name}_{timeframe}_{suffix}".strip('_'),
        trade_log=trade_log,
        metrics=metrics,
        capital_over_time=capital_over_time,
        output_dir=output_folder
    )

    try:
        plot_price_chart_with_indicators(
            df,
            name=f"{strategy_name}_{timeframe}_{suffix}".strip('_'),
            save_dir=output_folder,
            show=False
        )

        plot_equity_curve(
            capital_over_time,
            name=f"{strategy_name}_{timeframe}_{suffix}_equity_curve".strip('_'),
            save_dir=output_folder,
            show=False
        )
    except Exception as e:
        print(f"⚠️ Plotting error: {e}")

    print("\n" + "=" * 50 + "\n")


def main():
    print("\n" + "=" * 50)
    print("Initializing database...")
    init_db()
    print("Database initialized.")
    print("=" * 50 + "\n")

    df_original = get_data(SYMBOL, interval=INTERVAL, period=PERIOD)

    if df_original is None or df_original.empty or len(df_original) < 20:
        print("⚠️ Data not available or too short.")
        return

    print("Choose mode:")
    print("1: Run a single strategy")
    print("2: Parameter tuning (Grid Search) for Supertrend + RSI")
    print("3: Walk-forward validation")

    try:
        mode = input("Enter mode (1, 2 or 3): ").strip()
    except EOFError:
        mode = '1'

    if mode == '2':
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
            trading_fee_pct=TRADING_FEE_PCT,
            timeframe_minutes=convert_interval_to_minutes(INTERVAL)
        )

        if best:
            print("\n=== Best Parameter Set ===")
            print(best["params"])
            print_metrics(best["metrics"], name="Best Params")
        return

    if mode == '3':
        param_grid = {
            "rsi_period": [7, 14],
            "rsi_buy_threshold": [25, 30],
            "rsi_sell_threshold": [65, 70],
            "supertrend_period": [7, 10],
            "supertrend_multiplier": [2, 3]
        }

        results = walk_forward_validation(
            df_original,
            supertrend_rsi_strategy,
            param_grid=param_grid,
            n_splits=5,
            initial_capital=INITIAL_CAPITAL,
            stop_loss_pct=STOP_LOSS_PCT,
            take_profit_pct=TAKE_PROFIT_PCT,
            trading_fee_pct=TRADING_FEE_PCT,
            timeframe_minutes=convert_interval_to_minutes(INTERVAL),
            verbose=True
        )

        print("\n=== Walk-Forward Validation Results ===")
        for res in results:
            print(res)
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

    timeframes = ['5T', '15T', '1H', '1D']
    for tf in timeframes:
        print(f"\n{'=' * 50}\nBacktest for timeframe: {tf}\n{'=' * 50}\n")
        df_tf = df_original.copy() if tf == INTERVAL else resample_data(df_original, tf)
        df_in_sample, df_out_sample = split_data_for_out_of_sample(df_tf)
        print(f"Data split — In: {len(df_in_sample)}, Out: {len(df_out_sample)}")

        run_backtest_and_report(df_in_sample, strategy_func, strategy_name, tf, suffix="In-Sample")
        run_backtest_and_report(df_out_sample, strategy_func, strategy_name, tf, suffix="Out-of-Sample")

    print("✅ All backtests completed.")


if __name__ == "__main__":
    main()