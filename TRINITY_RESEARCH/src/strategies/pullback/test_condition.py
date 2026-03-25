import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

df = pd.read_csv("data/processed/stock/005930/data.csv")

cond = (
    (df["volume_ratio"] >= 2.0) &
    (df["body_ratio"] >= 0.5) &
    (df["is_breakout"] == True)
)

signals = df[cond]

print("신호 개수:", len(signals))
print(signals.head())