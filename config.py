# config.py

# General config
SYMBOL = "BTC-USD"
INTERVAL = "1h"
PERIOD = "30d"

# Supertrend default parameters
SUPERTREND_PERIOD = 10
SUPERTREND_MULTIPLIER = 3

# Advanced strategy params (if different, customize here)
ADV_SUPERTREND_PERIOD = 7
ADV_SUPERTREND_MULTIPLIER = 2

# Initial capital for backtest
INITIAL_CAPITAL = 1000

# Risk management: Stop Loss and Take Profit percentages (مثلاً 0.02 یعنی 2%)
STOP_LOSS_PCT = 0.02       # 2% حد ضرر
TAKE_PROFIT_PCT = 0.04     # 4% حد سود