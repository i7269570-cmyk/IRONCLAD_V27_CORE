import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import pandas as pd
from strategy import (
    MeanReversionBBStrategy_A,
    MeanReversionBBStrategy_B,
    MeanReversionBBStrategy_C
)

data_path = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\data\merged.csv"

df = pd.read_csv(data_path)
df.columns = [c.lower() for c in df.columns]

# =========================
# 지표 생성 (필수)
# =========================

# MA20
df["ma20"] = df["close"].rolling(20).mean()

# RSI
delta = df["close"].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss
df["rsi"] = 100 - (100 / (1 + rs))

# Bollinger
std = df["close"].rolling(20).std()
df["bb_middle"] = df["ma20"]
df["bb_lower"] = df["ma20"] - 2 * std


def run_backtest(strategy_class):

    all_returns = []

    for sym in df["symbol"].unique():
        sub = df[df["symbol"] == sym].copy()

        if len(sub) < 50:
            continue

        strategy = strategy_class()
        position = None

        for i in range(20, len(sub)):

            row = sub.iloc[i]

            if position is None:
                signal = strategy.on_bar(row, position)

                if signal == "BUY":
                    position = {
                        "entry_price": row["close"],
                        "hold_bars": 0
                    }

            else:
                signal = strategy.on_position(row, position)

                if signal == "EXIT":
                    exit_price = row["close"]

                    all_returns.append(
                        (exit_price - position["entry_price"]) / position["entry_price"]
                    )

                    position = None

    return pd.Series(all_returns)


def print_result(name, r):
    if len(r) == 0:
        print(f"\n{name} ❌ 거래 없음")
        return

    print(f"\n===== {name} =====")
    print("거래수:", len(r))
    print("승률:", round((r > 0).mean(), 3))
    print("PF:", round(r[r > 0].sum() / abs(r[r < 0].sum()), 3))
    print("평균:", round(r.mean(), 6))
    print("MDD:", round((r.cumsum().cummax() - r.cumsum()).max(), 4))


# 실행
rA = run_backtest(MeanReversionBBStrategy_A)
rB = run_backtest(MeanReversionBBStrategy_B)
rC = run_backtest(MeanReversionBBStrategy_C)

print_result("A (메인)", rA)
print_result("B (강화)", rB)
print_result("C (강화)", rC)


