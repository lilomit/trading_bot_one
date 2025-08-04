import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import pytest
from indicators import calculate_rsi, calculate_supertrend

def sample_df():
    data = {
        'Close': [100 + i for i in range(20)],
        'High': [101 + i for i in range(20)],
        'Low': [99 + i for i in range(20)],
    }
    return pd.DataFrame(data)

def test_calculate_rsi_valid():
    df = sample_df()
    result = calculate_rsi(df.copy(), window=14)
    assert 'RSI' in result.columns
    assert not result['RSI'].isnull().all()

def test_calculate_rsi_missing_close():
    df = sample_df().drop(columns=["Close"])
    with pytest.raises(ValueError):
        calculate_rsi(df)

def test_calculate_supertrend_valid():
    df = sample_df()
    result = calculate_supertrend(df.copy(), period=10, multiplier=3)
    assert 'Supertrend' in result.columns
    assert len(result) == len(df)

def test_calculate_supertrend_missing_column():
    df = sample_df().drop(columns=["High"])
    with pytest.raises(ValueError):
        calculate_supertrend(df)