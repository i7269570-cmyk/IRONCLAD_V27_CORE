import sys
import os
import pandas as pd

df = pd.read_csv("data/processed/stock/005930/data.csv")

cond = (
    (df["time"] >= 90000) &
    (df["time"] <= 91500) &
    (df["volume_ratio"] >= 3.0)
)

signals = df[cond]

print("신호 개수:", len(signals))