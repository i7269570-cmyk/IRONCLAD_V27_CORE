import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

BASE_DIR = "data/processed/stock"
FEE = 0.0015  # 0.15% 왕복

results = []

for symbol in os.listdir(BASE_DIR):
    file_path = os.path.join(BASE_DIR, symbol, "data.csv")

    try:
        df = pd.read_csv(file_path)

        # 종목별 평균 거래대금
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
                high = row["high"]
                low = row["low"]

                if low <= entry_price * (1 - 0.005):
                    exit_price = entry_price * (1 - 0.005)
                    break

                if high >= entry_price * (1 + 0.003):
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
            "count": len(trades),
            "avg_return": sum(trades) / len(trades)
        })

    except Exception as e:
        print(f"실패: {symbol} → {e}")

result_df = pd.DataFrame(results)

# 거래대금 상위 20개
top20 = result_df.sort_values("avg_value", ascending=False).head(20)

print("\n=== 거래대금 상위 20개 결과 ===")
print(top20[["symbol", "avg_value", "count", "avg_return"]])

print("\n=== 상위 20개 평균 수익 ===")
print(top20["avg_return"].mean())