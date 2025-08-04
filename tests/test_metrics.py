import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from metrics import calculate_metrics
from datetime import datetime, timedelta
import math

def generate_time_series(start, count, step_minutes, start_capital=1000, step_increase=10):
    return [(start + timedelta(minutes=step_minutes*i), start_capital + i*step_increase) for i in range(count)]

def test_calculate_metrics_with_typical_data():
    # داده نمونه با 3 معامله: 2 برد و 1 باخت
    time_series = generate_time_series(datetime(2023, 1, 1), 50, 5)
    trade_log = [
        {'profit_pct': 5},  # برد
        {'profit_pct': -2}, # باخت
        {'profit_pct': 3}   # برد
    ]

    result = calculate_metrics(time_series, trade_log, initial_capital=1000, timeframe_minutes=5)

    assert isinstance(result, dict)
    keys = [
        "Total Return (%)", "Annualized Return (%)", "Max Drawdown (%)", "Sharpe Ratio",
        "Win Rate (%)", "Profit Factor", "Average Trade Return (%)",
        "Calmar Ratio", "Sortino Ratio", "Expectancy", "Std Dev of Returns",
        "Avg Win / Avg Loss", "Max Consecutive Wins", "Max Consecutive Losses"
    ]
    for key in keys:
        assert key in result
        assert isinstance(result[key], (float, int)) or math.isnan(result[key])

    assert 0 <= result["Win Rate (%)"] <= 100
    assert result["Max Consecutive Wins"] >= 0
    assert result["Max Consecutive Losses"] >= 0

def test_calculate_metrics_all_wins():
    time_series = generate_time_series(datetime(2023, 1, 1), 10, 5)
    trade_log = [{'profit_pct': 2} for _ in range(10)]  # همه برد

    result = calculate_metrics(time_series, trade_log, initial_capital=1000, timeframe_minutes=5)

    assert result["Win Rate (%)"] == 100.0
    assert result["Profit Factor"] == float('inf') or result["Profit Factor"] > 1000  # چون ضرر صفر است، PF می‌تواند inf باشد
    assert result["Avg Win / Avg Loss"] == float('inf') or result["Avg Win / Avg Loss"] > 1000
    assert result["Max Consecutive Wins"] == 10
    assert result["Max Consecutive Losses"] == 0

def test_calculate_metrics_all_losses():
    time_series = generate_time_series(datetime(2023, 1, 1), 10, 5)
    trade_log = [{'profit_pct': -3} for _ in range(10)]  # همه باخت

    result = calculate_metrics(time_series, trade_log, initial_capital=1000, timeframe_minutes=5)

    assert result["Win Rate (%)"] == 0.0
    assert result["Profit Factor"] == 0.0
    assert result["Avg Win / Avg Loss"] == 0.0
    assert result["Max Consecutive Wins"] == 0
    assert result["Max Consecutive Losses"] == 10

def test_calculate_metrics_consecutive_mixed():
    # الگوی برد و باخت متناوب که max consecutive ها رو تست کنیم
    trade_log = [
        {'profit_pct': 1}, {'profit_pct': 2}, {'profit_pct': -1}, {'profit_pct': -2},
        {'profit_pct': -3}, {'profit_pct': 4}, {'profit_pct': 5}, {'profit_pct': 6},
        {'profit_pct': -1}, {'profit_pct': -1}
    ]
    time_series = generate_time_series(datetime(2023, 1, 1), len(trade_log), 5)

    result = calculate_metrics(time_series, trade_log, initial_capital=1000, timeframe_minutes=5)

    assert result["Max Consecutive Wins"] == 3  # 4,5,6 پشت سر هم
    assert result["Max Consecutive Losses"] == 3  # -1,-2,-3 پشت سر هم
    assert result["Avg Win / Avg Loss"] > 0

def test_calculate_metrics_empty_inputs():
    result = calculate_metrics([], [], initial_capital=1000)
    for key, value in result.items():
        assert (value == 0) or (isinstance(value, float) and math.isnan(value))