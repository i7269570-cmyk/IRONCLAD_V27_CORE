import sys
import os
import pandas as pd

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from strategy import (
    MeanReversionBBStrategy_A,
    MeanReversionBBStrategy_B,
    MeanReversionBBStrategy_C,
    MeanReversion_Disparity
)

# 1. 데이터 로드
data_path = r"data/merged.csv"
df = pd.read_csv(data_path)
df.columns = [c.lower() for c in df.columns]

print("📊 지표 생성 중...")

# 2. 지표 계산
df['ma20'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(20).mean())
df['std20'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(20).std())
df['bb_lower'] = df['ma20'] - (2 * df['std20'])
df['bb_middle'] = df['ma20']
df['volume_ma'] = df.groupby('symbol')['volume'].transform(lambda x: x.rolling(20).mean())
df['volume_ratio'] = df['volume'] / df['volume_ma']

# RSI 계산
delta = df.groupby('symbol')['close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.groupby(df['symbol']).transform(lambda x: x.rolling(14).mean())
avg_loss = loss.groupby(df['symbol']).transform(lambda x: x.rolling(14).mean())
df['rsi'] = 100 - (100 / (1 + (avg_gain / avg_loss)))

df = df.dropna()

# =========================
# 🔥 [NEW] 검증 데이터 분리 (최근 30% 구간)
# =========================
# 데이터의 가장 마지막 부분(최근 시장) 30%만 사용하여 검증
df = df.tail(int(len(df) * 0.3))

print(f"✅ 최근 데이터 검증 준비 완료 (데이터 수: {len(df)})")
input("👉 Enter 누르면 최근 시장 백테스트 시작")

# 3. 백테스트 엔진
def run_backtest(strategy_class):
    results = []
    for sym in df["symbol"].unique():
        sub = df[df["symbol"] == sym].copy().reset_index(drop=True)
        if len(sub) < 50: continue
        strategy = strategy_class()
        position = None
        for i in range(20, len(sub)):
            row = sub.iloc[i]
            if position is None:
                if strategy.on_bar(row, position) == "BUY":
                    position = {"entry_price": row["close"], "hold_bars": 0}
            else:
                if strategy.on_position(row, position) == "EXIT":
                    pnl = (row["close"] - position["entry_price"]) / position["entry_price"]
                    results.append(pnl)
                    position = None
    return pd.Series(results)

def print_result(name, r):
    if len(r) == 0:
        print(f"\n{name} ❌ 거래 없음"); return
    loss_sum = abs(r[r < 0].sum())
    pf = round(r[r > 0].sum() / loss_sum, 3) if loss_sum != 0 else "Inf"
    print(f"\n===== {name} (최근30% 검증) =====\n거래수: {len(r)} | 승률: {round((r > 0).mean(), 3)} | PF: {pf} | 평균: {round(r.mean(), 6)}")

# 4. 실행
rA = run_backtest(MeanReversionBBStrategy_A)
rB = run_backtest(MeanReversionBBStrategy_B)
rC = run_backtest(MeanReversionBBStrategy_C)
rDisp = run_backtest(MeanReversion_Disparity)

print_result("A", rA)
print_result("B", rB)
print_result("C", rC)
print_result("Disparity", rDisp)