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

        data = data.sort_values(["symbol", "date", "time"]).reset_index(drop=True)

        rows = data.to_dict("records")

        for i in range(len(rows) - 1):

            row = rows[i]
            next_row = rows[i + 1]

            # -----------------
            # 진입 신호
            # -----------------
            signal = self.strategy.on_bar(row, position)

            if position is None and signal == "BUY":

                # 🔥 다음 봉 시가로 진입
                entry_price = next_row["open"]* 1.003

                position = {
                    "entry_price": entry_price,
                    "entry_time": (next_row["date"], next_row["time"]),
                    "bars_held": 0
                }

                continue  # 같은 봉에서 exit 방지

            # -----------------
            # 보유 중
            # -----------------
            if position is not None:

                position["bars_held"] += 1

                exit_signal = self.strategy.on_position(row, position)

                if exit_signal is not None:

                    # 🔥 다음 봉 시가로 청산
                    exit_price = next_row["open"] * 0.997

                    pnl = (exit_price - position["entry_price"]) / position["entry_price"]
                    pnl = pnl - 0.002

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