import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

BASE_DIR = "data/processed/stock"
FEE = 0.0015

results = []

for symbol in os.listdir(BASE_DIR):

    file_path = os.path.join(BASE_DIR, symbol, "data.csv")

    try:
        df = pd.read_csv(file_path)

        cond = (
            (df["volume_ratio"] >= 2.5) &
            (df["body_ratio"] >= 0.5) &
            (df["is_breakout"] == True)
        )

        signals = df[cond]
        trades = []

        for idx in signals.index:

            future = df.loc[idx+1:idx+5]
            if len(future) == 0:
                continue

            entry_price = future["low"].min()
            exit_price = None

            for _, row in future.iterrows():

                if row["low"] <= entry_price * (1 - 0.005):
                    exit_price = entry_price * (1 - 0.005)
                    break

                if row["high"] >= entry_price * (1 + 0.003):
                    exit_price = entry_price * (1 + 0.003)
                    break

            if exit_price is None:
                exit_price = future.iloc[-1]["close"]

            ret = (exit_price / entry_price) - 1
            ret = ret - FEE
            trades.append(ret)

        if len(trades) == 0:
            continue

        avg_return = sum(trades) / len(trades)

        results.append({
            "symbol": symbol,
            "count": len(trades),
            "avg_return": avg_return
        })

    except:
        continue

result_df = pd.DataFrame(results)

# 상위 15개 종목 선택
top = result_df.sort_values("avg_return", ascending=False).head(15)

print("\n=== 수익 상위 종목 ===")
print(top)

print("\n=== 평균 수익 ===")
print(top["avg_return"].mean())