import itertools
from backtest import run_backtest
from metrics import calculate_metrics

def param_tuner(
    df,
    strategy_func,
    param_grid,
    initial_capital=1000,
    stop_loss_pct=None,
    take_profit_pct=None,
    timeframe_minutes=60
):
    keys = list(param_grid.keys())
    values = list(param_grid.values())
    all_combos = list(itertools.product(*values))

    results = []

    for combo in all_combos:
        params = dict(zip(keys, combo))

        try:
            df_strategy = strategy_func(df.copy(), **params)

            final_capital, trade_log, capital_over_time = run_backtest(
                df_strategy,
                initial_capital=initial_capital,
                stop_loss_pct=stop_loss_pct,
                take_profit_pct=take_profit_pct
            )

            metrics = calculate_metrics(
                capital_over_time,
                trade_log,
                initial_capital=initial_capital,
                timeframe_minutes=timeframe_minutes
            )
            metrics["Final Capital"] = final_capital

            results.append({
                "params": params,
                "metrics": metrics
            })

            print(f"Tested params: {params} -> Final Capital: {final_capital:.2f}")

        except Exception as e:
            print(f"Error with params {params}: {e}")

    results.sort(key=lambda x: x["metrics"]["Final Capital"], reverse=True)

    if results:
        best = results[0]
        print(f"\nBest params: {best['params']}")
        print(f"Metrics: {best['metrics']}")
        return best, results
    else:
        print("No successful runs.")
        return None, results