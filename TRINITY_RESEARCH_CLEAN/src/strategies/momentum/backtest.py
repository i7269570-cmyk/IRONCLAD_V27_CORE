import pandas as pd
import numpy as np
import glob

# ✅ Top 10 종목 고정
top_symbols = [
    "000150",
    "012450",
    "079550",
    "006800",
    "064350",
    "000720",
    "012330",
    "051910",
    "000660",
    "009150"
]

files = glob.glob("data/processed/stock/*/data.csv")

all_returns = []

for file in files:

    # 종목 코드 추출
    code = file.split("\\")[-2]

    # ✅ 종목 필터
    if code not in top_symbols:
        continue

    df = pd.read_csv(file)

    # ✅ 조건 (최종 확정)
    cond = (
        (df["time"] >= 90000) &
        (df["time"] <= 91500) &
        (df["volume_ratio"] >= 2.5)
    )

    returns = []

    for i in range(len(df) - 5):

        if cond.iloc[i]:

            entry = df.loc[i, "close"]
            future = df.iloc[i+1:i+6]

            tp = entry * 1.003
            sl = entry * 0.995

            if (future["high"] >= tp).any():
                returns.append(0.003)
            elif (future["low"] <= sl).any():
                returns.append(-0.005)
            else:
                exit_price = future.iloc[-1]["close"]
                returns.append((exit_price - entry) / entry)

    if len(returns) == 0:
        continue

    all_returns.extend(returns)

# ✅ 전체 결과
all_returns = np.array(all_returns)

print("=== 최종 결과 ===")
print("총 거래 수:", len(all_returns))
print("평균 수익:", all_returns.mean() if len(all_returns) > 0 else 0)
print("승률:", (all_returns > 0).mean() if len(all_returns) > 0 else 0)