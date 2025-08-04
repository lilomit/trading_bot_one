import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os
from config import SAVE_PLOTS, SHOW_PLOTS


def plot_price_chart_with_indicators(df, name="Price & Indicators", save_dir="results", show=False):
    df = df.copy()
    if 'Close' not in df.columns:
        print("⚠️ Warning: 'Close' column not found in dataframe. Cannot plot price chart.")
        return

    df = df.dropna(subset=["Close"])
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, errors='coerce')
        df = df.dropna(subset=["Close"])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

    ax1.plot(df.index, df['Close'], label='Close Price', color='gray', alpha=0.6)

    if 'Signal' in df.columns:
        ax1.scatter(df.index[df['Signal'] == 'buy'], df['Close'][df['Signal'] == 'buy'], marker='^', color='green', label='Buy Signal')
        ax1.scatter(df.index[df['Signal'] == 'sell'], df['Close'][df['Signal'] == 'sell'], marker='v', color='red', label='Sell Signal')

    if 'Supertrend' in df.columns and df['Supertrend'].dtype != 'bool':
        ax1.plot(df.index, df['Supertrend'], label='Supertrend', color='orange')

    ax1.set_ylabel("Price")
    ax1.legend()
    ax1.grid(True)
    ax1.set_title(name)

    if 'RSI' in df.columns:
        ax2.plot(df.index, df['RSI'], label='RSI', color='purple')
        ax2.axhline(70, color='red', linestyle='--', linewidth=1, label='Overbought (70)')
        ax2.axhline(30, color='green', linestyle='--', linewidth=1, label='Oversold (30)')
        ax2.set_ylabel("RSI")
        ax2.set_ylim(0, 100)
        ax2.legend()
        ax2.grid(True)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    plt.xticks(rotation=45)
    plt.tight_layout()

    if SAVE_PLOTS:
        os.makedirs(save_dir, exist_ok=True)
        filename = os.path.join(save_dir, f"{name.replace(' ', '_')}_price_chart.png")
        plt.savefig(filename)
        print(f"📈 Saved price chart to: {filename}")

    if show and SHOW_PLOTS:
        plt.show()

    plt.close()


def plot_equity_curve(capital_over_time, name="Equity Curve", save_dir="results", show=False):
    if not capital_over_time:
        print("⚠️ No capital data to plot equity curve.")
        return

    times, capitals = zip(*capital_over_time)

    plt.figure(figsize=(16, 5))
    plt.plot(times, capitals, label='Equity Curve', color='blue', linewidth=2)
    plt.title("📈 Equity Curve")
    plt.xlabel("Time")
    plt.ylabel("Capital")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    plt.gcf().autofmt_xdate()
    plt.tight_layout()

    if SAVE_PLOTS:
        os.makedirs(save_dir, exist_ok=True)
        filename = os.path.join(save_dir, f"{name.replace(' ', '_')}_equity_curve.png")
        plt.savefig(filename)
        print(f"📉 Saved equity curve to: {filename}")

    if show and SHOW_PLOTS:
        plt.show()

    plt.close()