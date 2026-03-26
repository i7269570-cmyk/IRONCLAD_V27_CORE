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

        avg_value = df["value"].mean()

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

        results.append({
            "symbol": symbol,
            "avg_value": avg_value,
            "avg_return": sum(trades) / len(trades)
        })

    except:
        continue

result_df = pd.DataFrame(results)

# 중간 구간 (예: 400 ~ 2000)
filtered = result_df[
    (result_df["avg_value"] > 400) &
    (result_df["avg_value"] < 2000)
]

print("\n=== 중간 거래대금 종목 ===")
print(filtered.sort_values("avg_return", ascending=False))

print("\n=== 평균 수익 ===")
print(filtered["avg_return"].mean())