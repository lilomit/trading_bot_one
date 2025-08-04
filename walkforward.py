import pandas as pd
from collections import Counter
from utils.split import split_data_for_out_of_sample
from param_tuner import param_tuner
from backtest import run_backtest
from metrics import calculate_metrics
from utils.file import create_output_folder, get_filepath

def summarize_results(results, verbose=True):
    """
    نمایش خلاصه کلی نتایج Walk-Forward

    پارامتر:
    - results: لیست دیکشنری‌های متریک‌ها
    """
    if not results:
        if verbose:
            print("⚠️ هیچ نتیجه‌ای برای خلاصه وجود ندارد.")
        return

    df = pd.DataFrame(results)

    # محاسبه میانگین و میانه بازده نهایی (Total Return %)
    mean_return = df['Total Return (%)'].mean()
    median_return = df['Total Return (%)'].median()

    if verbose:
        print("\n📊 خلاصه نتایج Walk-Forward Validation:")
        print(f"میانگین بازده کل: {mean_return:.2f}%")
        print(f"میانه بازده کل: {median_return:.2f}%")

    # پیدا کردن پارامترهای پرتکرار
    params_list = df["Best Params"].tolist()
    # هر param دیکشنریه؛ تبدیل به tuple برای شمارش
    params_tuples = [tuple(sorted(p.items())) for p in params_list]
    counter = Counter(params_tuples)

    most_common_params = counter.most_common(3)

    if verbose:
        print("\n🔥 بهترین پارامترهای پرتکرار:")
        for params, count in most_common_params:
            param_dict = dict(params)
            print(f"تکرار: {count} بار — پارامترها: {param_dict}")

    return {
        "mean_return": mean_return,
        "median_return": median_return,
        "most_common_params": [(dict(p[0]), p[1]) for p in most_common_params]
    }

def walk_forward_validation(
    df,
    strategy_func,
    param_grid,
    n_splits=5,
    initial_capital=1000,
    stop_loss_pct=0.03,
    take_profit_pct=0.05,
    trading_fee_pct=0.001,
    timeframe_minutes=60,
    verbose=True,
    save_results_to_file=True
):
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    df = df.sort_index()
    total_len = len(df)
    step_size = total_len // n_splits

    results = []

    min_supertrend_period = min(param_grid.get('supertrend_period', [7]))
    min_rsi_period = 14
    min_period_needed = max(min_supertrend_period, min_rsi_period)

    for i in range(n_splits):
        start = 0
        mid = start + step_size * (i + 1)
        end = mid + step_size

        df_in = df.iloc[start:mid].copy()
        df_out = df.iloc[mid:end].copy()

        if df_out.empty or df_in.empty:
            break

        if verbose:
            print(f"\n🧪 Split {i + 1}/{n_splits} → in: {df_in.shape[0]} rows | out: {df_out.shape[0]} rows")

        if len(df_out) < min_period_needed:
            if verbose:
                print(f"⚠️ Split {i + 1} skipped: داده‌ی out-of-sample کمتر از حداقل دوره لازم ({min_period_needed}) است.")
            continue

        best_result, _ = param_tuner(
            df_in,
            strategy_func,
            param_grid,
            initial_capital=initial_capital,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            trading_fee_pct=trading_fee_pct,
            timeframe_minutes=timeframe_minutes,
            verbose=False
        )

        if best_result is None:
            if verbose:
                print("⛔ No best parameters found in this split.")
            continue

        best_params = best_result["params"]
        if verbose:
            print(f"✅ Best Params: {best_params}")

        df_out_with_signals = strategy_func(df_out.copy(), **best_params)

        final_capital, trade_log, capital_over_time, _ = run_backtest(
            df_out_with_signals,
            initial_capital=initial_capital,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            trading_fee_pct=trading_fee_pct
        )

        metrics = calculate_metrics(
            capital_over_time,
            trade_log,
            initial_capital=initial_capital,
            timeframe_minutes=timeframe_minutes
        )
        metrics["Final Capital"] = final_capital
        metrics["Split"] = i + 1
        metrics["Best Params"] = best_params

        results.append(metrics)

    if save_results_to_file and results:
        output_folder = create_output_folder(strategy_name="walkforward")
        df_results = pd.DataFrame(results)
        csv_path = get_filepath(output_folder, "walkforward_results.csv")
        df_results.to_csv(csv_path, index=False)
        if verbose:
            print(f"\n💾 Walk-Forward results saved to CSV: {csv_path}")

        json_path = get_filepath(output_folder, "walkforward_results.json")
        df_results.to_json(json_path, orient='records', date_format='iso')
        if verbose:
            print(f"💾 Walk-Forward results saved to JSON: {json_path}")

    # نمایش خلاصه نتایج
    summarize_results(results, verbose=verbose)

    return results