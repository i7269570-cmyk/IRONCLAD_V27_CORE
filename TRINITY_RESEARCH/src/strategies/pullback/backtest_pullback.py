import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

df = pd.read_csv("data/processed/stock/005930/data.csv")

# 기존 조건
cond = (
    (df["volume_ratio"] >= 2.5) &
    (df["body_ratio"] >= 0.5) &
    (df["is_breakout"] == True)
)

signals = df[cond]

results = []

for idx in signals.index:

    # 다음 3봉 중 저가 눌림 확인
    future = df.loc[idx+1:idx+3]

    if len(future) == 0:
        continue

    entry_price = future["low"].min()
    exit_price = df.loc[idx+3, "close"] if idx+3 in df.index else None

    if exit_price is None:
        continue

    ret = (exit_price / entry_price) - 1
    results.append(ret)

print("평균 수익:", sum(results)/len(results))
print("거래 수:", len(results))