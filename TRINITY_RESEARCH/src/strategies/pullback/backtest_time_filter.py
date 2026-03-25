import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

BASE_DIR = "data/processed/stock"
FEE = 0.0015

def get_time_group(t):
    t = int(t)

    if 90000 <= t < 93000:
        return "A_0900"
    elif 93000 <= t < 103000:
        return "B_0930"
    elif 103000 <= t < 113000:
        return "C_1030"
    elif 130000 <= t < 143000:
        return "D_1300"
    else:
        return None

results = {}

for symbol in os.listdir(BASE_DIR):

    file_path = os.path.join(BASE_DIR, symbol, "data.csv")

    try:
        df = pd.read_csv(file_path)

        # 성과 상위 종목 필터 (이미 검증된 종목만)
        # 여기서는 전체 돌리고 나중에 종목 필터 적용

        cond = (
            (df["volume_ratio"] >= 2.5) &
            (df["body_ratio"] >= 0.5) &
            (df["is_breakout"] == True)
        )

        signals = df[cond]

        for idx in signals.index:

            time = df.loc[idx, "time"]
            group = get_time_group(time)

            if group is None:
                continue

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

            if group not in results:
                results[group] = []

            results[group].append(ret)

    except:
        continue

print("\n=== 시간대별 결과 ===")

for k, v in results.items():
    if len(v) == 0:
        continue

    avg = sum(v) / len(v)

    print(f"{k} → 거래수={len(v)}, 평균수익={avg:.6f}")