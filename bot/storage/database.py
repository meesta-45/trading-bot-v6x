import sqlite3
from datetime import datetime


class TradeDB:

    def __init__(self, path="trades.db"):

        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            strategy TEXT,
            direction TEXT,
            confidence REAL,
            score REAL,
            regime TEXT,
            pnl REAL
        )
        """)

        self.conn.commit()

    def log_trade(self, strategy, direction, confidence, score, regime, pnl):

        self.cursor.execute("""
        INSERT INTO trades (
            timestamp, strategy, direction,
            confidence, score, regime, pnl
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            strategy,
            direction,
            confidence,
            score,
            regime,
            pnl
        ))

        self.conn.commit()
