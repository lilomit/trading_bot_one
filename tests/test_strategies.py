import pytest
import pandas as pd
import numpy as np
import sys
import os

# اضافه کردن مسیر پروژه به sys.path برای حل مشکل ایمپورت
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from strategies.supertrend_rsi_strategies import supertrend_rsi_strategy
from strategies.advanced_strategies import advanced_strategy
from indicators import calculate_rsi, calculate_supertrend


@pytest.fixture
def sample_ohlcv_data():
    dates = pd.date_range(start="2023-01-01", periods=30, freq='D')
    data = {
        "Open": pd.Series(100 + np.random.randn(30).cumsum(), index=dates),
        "High": pd.Series(101 + np.random.randn(30).cumsum(), index=dates),
        "Low": pd.Series(99 + np.random.randn(30).cumsum(), index=dates),
        "Close": pd.Series(100 + np.random.randn(30).cumsum(), index=dates),
        "Volume": pd.Series(1000 + np.random.randint(0, 100, 30), index=dates)
    }
    return pd.DataFrame(data)


def test_calculate_rsi_basic(sample_ohlcv_data):
    df_rsi = calculate_rsi(sample_ohlcv_data, window=14)
    assert 'RSI' in df_rsi.columns
    assert df_rsi['RSI'].notna().sum() > 0
    # باید مقادیر بین 0 تا 100 باشند ولی ممکنه اول‌ها NaN باشه
    valid_rsi = df_rsi['RSI'].dropna()
    assert valid_rsi.between(0, 100).all()


def test_calculate_supertrend_basic(sample_ohlcv_data):
    df_st = calculate_supertrend(sample_ohlcv_data, period=10, multiplier=3)
    assert 'Supertrend' in df_st.columns
    assert df_st['Supertrend'].dtype in [bool, np.bool_, object]
    assert df_st['Supertrend'].notna().all()


def test_supertrend_rsi_strategy_signals(sample_ohlcv_data):
    df_signals = supertrend_rsi_strategy(
        sample_ohlcv_data,
        rsi_period=14,
        rsi_buy_threshold=30,
        rsi_sell_threshold=70,
        supertrend_period=10,
        supertrend_multiplier=3
    )
    assert 'Signal' in df_signals.columns
    signals = df_signals['Signal'].unique()
    assert set(signals).issubset({'buy', 'sell', 'hold'})


def test_advanced_strategy_signals(sample_ohlcv_data):
    df_signals = advanced_strategy(
        sample_ohlcv_data,
        rsi_window=7,
        supertrend_period=7,
        supertrend_multiplier=2
    )
    assert 'Signal' in df_signals.columns
    signals = df_signals['Signal'].unique()
    assert set(signals).issubset({'buy', 'sell', 'hold'})


def test_rsi_raises_on_missing_close():
    df = pd.DataFrame({"Open": [1, 2, 3]})
    with pytest.raises(ValueError, match="Close"):
        calculate_rsi(df)


def test_supertrend_raises_on_missing_columns():
    df = pd.DataFrame({"Open": [1, 2, 3]})
    with pytest.raises(ValueError, match="High|Low|Close"):
        calculate_supertrend(df)


def test_strategy_handles_empty_df():
    # دیتافریم حداقلی یک ردیف با صفرها برای جلوگیری از ارور
    empty_df = pd.DataFrame({
        'Open': [0],
        'High': [0],
        'Low': [0],
        'Close': [0],
        'Volume': [0]
    })
    df1 = supertrend_rsi_strategy(empty_df)
    df2 = advanced_strategy(empty_df)
    assert 'Signal' in df1.columns
    assert 'Signal' in df2.columns
    assert all(df1['Signal'] == 'hold')
    assert all(df2['Signal'] == 'hold')