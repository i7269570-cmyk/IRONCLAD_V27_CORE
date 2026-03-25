import pandas as pd


class BacktestEngine:

    def __init__(self, strategy, initial_cash=10_000_000):
        self.strategy = strategy
        self.initial_cash = initial_cash

    def run(self, data):

        trades = []
        equity_curve = []

        cash = self.initial_cash
        position = None

        data = data.sort_values(["symbol", "date", "time"])

        for idx, row in data.iterrows():
            
            signal = self.strategy.on_bar(row, position)
            
            # -----------------
            # 진입
            # -----------------
            if position is None and signal == "BUY":

                entry_price = row["close"]

                position = {
                    "entry_price": entry_price,
                    "entry_time": (row["date"], row["time"]),
                    "bars_held": 0
                }

            # -----------------
            # 보유 중
            # -----------------
            elif position is not None:

                position["bars_held"] += 1

                exit_signal = self.strategy.on_position(row, position)

                if exit_signal is not None:

                    exit_price = row["close"]

                    pnl = (exit_price - position["entry_price"]) / position["entry_price"]

                    cash = cash * (1 + pnl)

                    trades.append({
                        "entry_price": position["entry_price"],
                        "exit_price": exit_price,
                        "pnl": pnl,
                        "bars": position["bars_held"]
                    })

                    position = None

            equity_curve.append(cash)

        trades_df = pd.DataFrame(trades)
        equity_df = pd.DataFrame({"equity": equity_curve})

        return {
            "trades": trades_df,
            "equity_curve": equity_df
        }