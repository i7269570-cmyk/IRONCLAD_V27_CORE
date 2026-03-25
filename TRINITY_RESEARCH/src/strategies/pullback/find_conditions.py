import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

df = pd.read_csv("data/processed/stock/005930/data.csv")

results = []

volume_list = [1.5, 2.0, 2.5, 3.0]
body_list = [0.3, 0.5, 0.7]

for v in volume_list:
    for b in body_list:

        cond = (
            (df["volume_ratio"] >= v) &
            (df["body_ratio"] >= b) &
            (df["is_breakout"] == True)
        )

        signals = df[cond]

        results.append({
            "volume_ratio": v,
            "body_ratio": b,
            "count": len(signals)
        })

result_df = pd.DataFrame(results)

result_df = result_df.sort_values("count", ascending=False)

print(result_df)