# config.py

# ==========================
# 💼 General Configuration
# ==========================

SYMBOL = "BTC-USD"         # نماد دارایی (مثل BTC-USD)
INTERVAL = "1h"            # تایم‌فریم (مثلاً: "5T", "15T", "1H", "1D")
PERIOD = "30d"             # بازه زمانی دریافت داده (مثل "30d" یعنی ۳۰ روز اخیر)


# ==========================
# 💰 Capital & Risk Settings
# ==========================

INITIAL_CAPITAL = 1000     # سرمایه اولیه برای بک‌تست (به دلار)

STOP_LOSS_PCT = 0.02       # حد ضرر ۲٪
TAKE_PROFIT_PCT = 0.04     # حد سود ۴٪

TRADING_FEE_PCT = 0.001    # کارمزد ۰.۱٪ (یعنی ۰.۰۰۱)


# ==========================
# 📈 Strategy Parameters
# ==========================

# --- برای استراتژی ساده Supertrend + RSI
SUPERTREND_PERIOD = 10
SUPERTREND_MULTIPLIER = 3

RSI_PERIOD = 14
RSI_BUY_THRESHOLD = 30
RSI_SELL_THRESHOLD = 70

# --- برای استراتژی پیشرفته‌تر (Advanced)
ADV_SUPERTREND_PERIOD = 7
ADV_SUPERTREND_MULTIPLIER = 2


# ==========================
# 🖼️ Plotting & Export Options
# ==========================

SAVE_PLOTS = True      # اگر True باشد، نمودارها ذخیره می‌شوند
SHOW_PLOTS = False     # اگر True باشد، نمودارها نمایش داده می‌شوند (plt.show)

SAVE_RESULTS = True    # اگر True باشد، نتایج در فایل ذخیره می‌شوند (CSV/JSON)