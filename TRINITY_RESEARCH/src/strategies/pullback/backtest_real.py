import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

BASE_DIR = "data/processed/stock"

symbols = os.listdir(BASE_DIR)

FEE = 0.0015   # 0.15% (왕복)

results = []

for symbol in symbols:

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

                high = row["high"]
                low = row["low"]

                # 손절 -0.5%
                if low <= entry_price * (1 - 0.005):
                    exit_price = entry_price * (1 - 0.005)
                    break

                # 익절 +0.3%
                if high >= entry_price * (1 + 0.003):
                    exit_price = entry_price * (1 + 0.003)
                    break

            if exit_price is None:
                exit_price = future.iloc[-1]["close"]

            ret = (exit_price / entry_price) - 1

            # 수수료 반영
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

    except Exception as e:
        print(f"실패: {symbol} → {e}")

result_df = pd.DataFrame(results)

print("\n=== 종목별 결과 ===")
print(result_df.sort_values("avg_return", ascending=False))

print("\n=== 전체 평균 ===")
print(result_df["avg_return"].mean())