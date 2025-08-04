import os
import json
import pandas as pd


def format_trade_log(trade_log):
    lines = []
    if not trade_log:
        lines.append("No trades executed.\n")
        return lines

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
            line = f"Entry: {etime} @ {ep:,.2f} | Exit: {xtime} @ {xp:,.2f} | Volume: {vol} | Profit: {prof_str} | Reason: {reason}"
            lines.append(line)
        else:
            lines.append(str(log))
    return lines


def format_metrics(metrics):
    lines = []
    lines.append(f"💰 Final Capital: {metrics.get('Final Capital', 0):,.2f} USD")
    lines.append(f"\n📊 Backtest Metrics:")
    for key, value in metrics.items():
        if key == "Final Capital":
            continue
        if isinstance(value, (int, float)):
            lines.append(f"{key}: {value:.2f}")
        else:
            lines.append(f"{key}: {value}")
    return lines


def print_trade_log(trade_log, name="Strategy"):
    print(f"\n📋 Trade Log ({name}):")
    for line in format_trade_log(trade_log):
        print(line)


def print_metrics(metrics, name="Strategy"):
    print(f"\n📊 Metrics ({name}):")
    for line in format_metrics(metrics):
        print(line)
    print("\n" + "=" * 50 + "\n")


def save_results(strategy_name, trade_log, metrics, capital_over_time, output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)
    safe_name = strategy_name.replace(' ', '_')

    trade_log_path = os.path.join(output_dir, f"trade_log_{safe_name}.csv")
    metrics_path = os.path.join(output_dir, f"metrics_{safe_name}.json")
    equity_path = os.path.join(output_dir, f"equity_curve_{safe_name}.csv")

    if len(trade_log) > 0 and isinstance(trade_log[0], dict):
        pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)
    else:
        pd.DataFrame({'Log': trade_log}).to_csv(trade_log_path, index=False)

    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)

    capital_df = pd.DataFrame(capital_over_time, columns=['Time', 'Capital'])
    capital_df.to_csv(equity_path, index=False)

    print(f"✅ Results saved to '{output_dir}' folder.")