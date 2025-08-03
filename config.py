# config.py

# General config
SYMBOL = "BTC-USD"         # نماد ارز دیجیتال یا دارایی
INTERVAL = "1h"            # تایم‌فریم داده‌ها (مثلاً: "5T", "15T", "1H", "1D")
PERIOD = "30d"             # بازه‌ی زمانی برای دریافت داده‌ها (مثلاً: "30d" یعنی ۳۰ روز گذشته)

# Initial capital for backtest
INITIAL_CAPITAL = 1000     # سرمایه اولیه برای بک‌تست

# Risk management: Stop Loss and Take Profit percentages
STOP_LOSS_PCT = 0.02       # 2% حد ضرر
TAKE_PROFIT_PCT = 0.04     # 4% حد سود

# Trading fee percentage
TRADING_FEE_PCT = 0.001    # 0.1% کارمزد معاملات

# Supertrend default parameters (برای استراتژی ساده)
SUPERTREND_PERIOD = 10
SUPERTREND_MULTIPLIER = 3

# RSI default parameters
RSI_PERIOD = 14
RSI_BUY_THRESHOLD = 30
RSI_SELL_THRESHOLD = 70

# Advanced strategy params (در صورت نیاز به تنظیم متفاوت)
ADV_SUPERTREND_PERIOD = 7
ADV_SUPERTREND_MULTIPLIER = 2