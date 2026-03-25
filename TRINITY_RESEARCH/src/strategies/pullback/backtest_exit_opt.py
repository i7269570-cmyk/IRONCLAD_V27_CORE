import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

df = pd.read_csv("data/processed/stock/005930/data.csv")

# ENTRY 조건 (고정)
entry_cond = (
    (df["volume_ratio"] >= 2.5) &
    (df["body_ratio"] >= 0.5) &
    (df["is_breakout"] == True)
)

signals = df[entry_cond]

stop_list = [0.003, 0.005, 0.01]
tp_list = [0.003, 0.005, 0.01]
hold_list = [1, 3, 5]

results = []

for stop in stop_list:
    for tp in tp_list:
        for hold in hold_list:

            trades = []

            for idx in signals.index:

                future = df.loc[idx+1:idx+hold]

                if len(future) == 0:
                    continue

                entry_price = future["low"].min()

                exit_price = None

                for _, row in future.iterrows():

                    high = row["high"]
                    low = row["low"]

                    # 손절
                    if low <= entry_price * (1 - stop):
                        exit_price = entry_price * (1 - stop)
                        break

                    # 익절
                    if high >= entry_price * (1 + tp):
                        exit_price = entry_price * (1 + tp)
                        break

                # 시간 종료
                if exit_price is None:
                    exit_price = future.iloc[-1]["close"]

                ret = (exit_price / entry_price) - 1
                trades.append(ret)

            if len(trades) == 0:
                continue

            avg_return = sum(trades) / len(trades)

            results.append({
                "stop": stop,
                "tp": tp,
                "hold": hold,
                "count": len(trades),
                "avg_return": avg_return
            })

result_df = pd.DataFrame(results)

result_df = result_df.sort_values("avg_return", ascending=False)

print(result_df.head(10))