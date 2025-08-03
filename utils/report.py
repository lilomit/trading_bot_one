import os
import json
import pandas as pd

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
            if isinstance(value, (int, float)):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
    print("\n" + "=" * 50 + "\n")

def save_results(strategy_name, trade_log, metrics, capital_over_time):
    os.makedirs("results", exist_ok=True)

    safe_name = strategy_name.replace(' ', '_')

    if len(trade_log) > 0 and isinstance(trade_log[0], dict):
        pd.DataFrame(trade_log).to_csv(f"results/trade_log_{safe_name}.csv", index=False)
    else:
        pd.DataFrame({'Log': trade_log}).to_csv(f"results/trade_log_{safe_name}.csv", index=False)

    with open(f"results/metrics_{safe_name}.json", "w") as f:
        json.dump(metrics, f, indent=4)

    capital_df = pd.DataFrame(capital_over_time, columns=['Time', 'Capital'])
    capital_df.to_csv(f"results/equity_curve_{safe_name}.csv", index=False)

    print(f"✅ Results saved to 'results/' folder.")