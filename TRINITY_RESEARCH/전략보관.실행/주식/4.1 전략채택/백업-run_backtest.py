import sys
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from strategy import (
    MeanReversionBBStrategy_A,
    MeanReversionBBStrategy_B,
    MeanReversionBBStrategy_C,
)

data_path = r"data/merged.csv"
df = pd.read_csv(data_path)
df.columns = [c.lower() for c in df.columns]

print("📊 지표 생성 중...")

# =========================
# 지표 계산 (필수)
# =========================
df['ma20'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(20).mean())

df['std20'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(20).std())
df['bb_upper'] = df['ma20'] + (2 * df['std20'])
df['bb_lower'] = df['ma20'] - (2 * df['std20'])
df['bb_middle'] = df['ma20']

delta = df.groupby('symbol')['close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)

avg_gain = gain.groupby(df['symbol']).transform(lambda x: x.rolling(14).mean())
avg_loss = loss.groupby(df['symbol']).transform(lambda x: x.rolling(14).mean())

rs = avg_gain / avg_loss
df['rsi'] = 100 - (100 / (1 + rs))

df = df.dropna()

# =========================
# 🔥 검증 데이터 분리 (핵심)
# =========================
start = int(len(df) * 0.3)
end   = int(len(df) * 0.7)
df = df.iloc[start:end]

print("✅ 검증 데이터 준비 완료")

input("👉 Enter 누르면 백테스트 시작")


# =========================
# 백테스트
# =========================
def run_backtest(strategy_class):
    results = []

    for sym in df["symbol"].unique():
        sub = df[df["symbol"] == sym].copy().reset_index(drop=True)
        if len(sub) < 50:
            continue

        strategy = strategy_class()
        position = None

        for i in range(20, len(sub)):
            row = sub.iloc[i]

            if position is None:
                signal = strategy.on_bar(row, position)
                if signal == "BUY":
                    position = {"entry_price": row["close"], "hold_bars": 0}

            else:
                signal = strategy.on_position(row, position)
                if signal == "EXIT":
                    pnl = (row["close"] - position["entry_price"]) / position["entry_price"]
                    results.append(pnl)
                    position = None

    return pd.Series(results)


def print_result(name, r):
    if len(r) == 0:
        print(f"\n{name} ❌ 거래 없음")
        return

    print(f"\n===== {name} =====")
    print("거래수:", len(r))
    print("승률:", round((r > 0).mean(), 3))

    loss_sum = abs(r[r < 0].sum())
    pf = round(r[r > 0].sum() / loss_sum, 3) if loss_sum != 0 else "Inf"

    print("PF:", pf)
    print("평균:", round(r.mean(), 6))
    print("MDD:", round((r.cumsum().cummax() - r.cumsum()).max(), 4))


# =========================
# 실행
# =========================
rB = run_backtest(MeanReversionBBStrategy_B)
print_result("B (검증)", rB)