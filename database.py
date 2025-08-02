import sqlite3
from contextlib import closing
import os

DB_FILE = "results/trading_bot.db"

def init_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with closing(sqlite3.connect(DB_FILE)) as conn:
        c = conn.cursor()
        # جدول معاملات
        c.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_time TEXT,
            exit_time TEXT,
            entry_price REAL,
            exit_price REAL,
            volume REAL,
            profit_pct REAL,
            reason TEXT
        )
        """)

        # جدول متریک‌ها
        c.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_time TEXT,
            total_return REAL,
            annualized_return REAL,
            max_drawdown REAL,
            sharpe_ratio REAL,
            win_rate REAL,
            profit_factor REAL,
            avg_trade_return REAL
        )
        """)
        conn.commit()

def save_trade(trade):
    with closing(sqlite3.connect(DB_FILE)) as conn:
        c = conn.cursor()
        c.execute("""
        INSERT INTO trades (entry_time, exit_time, entry_price, exit_price, volume, profit_pct, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            trade.get("entry_time"),
            trade.get("exit_time"),
            trade.get("entry_price"),
            trade.get("exit_price"),
            trade.get("volume"),
            trade.get("profit_pct"),
            trade.get("reason")
        ))
        conn.commit()

def save_metrics(metrics, run_time):
    with closing(sqlite3.connect(DB_FILE)) as conn:
        c = conn.cursor()
        c.execute("""
        INSERT INTO metrics (run_time, total_return, annualized_return, max_drawdown, sharpe_ratio, win_rate, profit_factor, avg_trade_return)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_time,
            metrics.get("Total Return (%)"),
            metrics.get("Annualized Return (%)"),
            metrics.get("Max Drawdown (%)"),
            metrics.get("Sharpe Ratio"),
            metrics.get("Win Rate (%)"),
            metrics.get("Profit Factor"),
            metrics.get("Average Trade Return (%)")
        ))
        conn.commit()