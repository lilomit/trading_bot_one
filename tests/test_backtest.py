import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
from backtest import run_backtest


@pytest.fixture
def sample_data_with_signals():
    data = {
        "Close": [100, 102, 101, 105, 103],
        "Low": [99, 101, 100, 104, 102],
        "High": [101, 103, 102, 106, 104],
        "Signal": ['buy', '', '', 'sell', '']
    }
    index = pd.date_range(start="2022-01-01", periods=5, freq='1h')
    return pd.DataFrame(data, index=index)


@pytest.fixture
def sample_data_no_signals():
    data = {
        "Close": [100, 101, 102, 103, 104],
        "Low": [99, 100, 101, 102, 103],
        "High": [101, 102, 103, 104, 105],
        "Signal": ['hold', 'hold', 'hold', 'hold', 'hold']
    }
    index = pd.date_range(start="2022-01-01", periods=5, freq='1h')
    return pd.DataFrame(data, index=index)


def test_run_backtest_with_signals(sample_data_with_signals):
    final_capital, trade_log, capital_over_time, total_fees = run_backtest(
        sample_data_with_signals,
        initial_capital=1000.0,
        stop_loss_pct=0.05,
        take_profit_pct=0.05,
        trading_fee_pct=0.001
    )

    assert isinstance(final_capital, float)
    assert isinstance(trade_log, list)
    assert isinstance(capital_over_time, list)
    assert isinstance(total_fees, float)

    assert len(trade_log) > 0
    assert "entry_price" in trade_log[0]
    assert "exit_price" in trade_log[0] or trade_log[0]["exit_price"] is None


def test_run_backtest_no_trades(sample_data_no_signals):
    final_capital, trade_log, capital_over_time, total_fees = run_backtest(
        sample_data_no_signals,
        initial_capital=1000.0,
        stop_loss_pct=0.05,
        take_profit_pct=0.05,
        trading_fee_pct=0.001
    )

    # انتظار داریم هیچ تریدی انجام نشده باشه
    assert isinstance(final_capital, float)
    assert isinstance(trade_log, list)
    assert isinstance(capital_over_time, list)
    assert isinstance(total_fees, float)

    assert len(trade_log) == 0
    assert final_capital == 1000.0 or final_capital > 0