import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.time import convert_interval_to_minutes, convert_interval_to_pandas_freq

def test_convert_interval_to_minutes():
    assert convert_interval_to_minutes("1T") == 1
    assert convert_interval_to_minutes("15T") == 15
    assert convert_interval_to_minutes("1H") == 60
    assert convert_interval_to_minutes("1D") == 1440

def test_convert_interval_to_pandas_freq():
    assert convert_interval_to_pandas_freq("1T") == "1min"
    assert convert_interval_to_pandas_freq("15T") == "15min"
    assert convert_interval_to_pandas_freq("1H") == "1h"
    assert convert_interval_to_pandas_freq("1D") == "1d"