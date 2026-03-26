import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

df = pd.read_csv("data/processed/stock/005930/data.csv")

tests = [
    (3.0, 0.5),
    (2.0, 0.7),
    (2.5, 0.7),
    (3.0, 0.7)
]

for v, b in tests:

    cond = (
        (df["volume_ratio"] >= v) &
        (df["body_ratio"] >= b) &
        (df["is_breakout"] == True)
    )

    signals = df[cond]

    # 다음 봉 수익
    signals["next_return"] = df["close"].shift(-1) / df["close"] - 1

    avg_return = signals["next_return"].mean()

    print(f"조건 v={v}, b={b} → 개수={len(signals)}, 평균수익={avg_return:.4f}")