import random
from bot.config import MODE

class ExecutionEngine:

    def execute(self, symbol, signal):

        if MODE == "PAPER":
            return random.choice(["WIN", "LOSS"])

        elif MODE == "DEMO":
            print(f"[DEMO TRADE] {symbol} {signal}")
            return "WIN"

        elif MODE == "LIVE":
            print(f"[LIVE TRADE READY] {symbol} {signal}")
            return "PENDING"
