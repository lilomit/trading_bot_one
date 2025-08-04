import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
from param_tuner import param_tuner

def dummy_strategy(df, rsi_period):
    df['Signal'] = ['buy'] + [''] * (len(df) - 1)
    return df

@pytest.fixture
def sample_data():
    data = {
        "Close": [100, 101, 102, 103, 104],
        "Low": [99, 100, 101, 102, 103],
        "High": [101, 102, 103, 104, 105],
    }
    index = pd.date_range(start="2022-01-01", periods=5, freq='1h')
    return pd.DataFrame(data, index=index)

def test_param_tuner_runs(sample_data):
    param_grid = {
        "rsi_period": [5, 10]
    }

    best_result, all_results = param_tuner(
        df=sample_data,
        strategy_func=dummy_strategy,
        param_grid=param_grid,
        timeframe_minutes=60
    )

    assert best_result is not None
    assert isinstance(best_result, dict)
    assert "params" in best_result
    assert "metrics" in best_result
    assert len(all_results) == 2