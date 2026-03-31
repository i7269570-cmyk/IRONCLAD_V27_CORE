import sys
import os
import pandas as pd

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from strategy import (
    VolatilityBreakout_A,
    VolatilityBreakout_B,
    VolatilityBreakout_C,
)

data_path = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\data\merged.csv"
df = pd.read_csv(data_path)
df.columns = [c.lower() for c in df.columns]

# ============================================================
# [지표 생성 순서 엄격 준수] - KeyError 방지 및 연산 최적화
# ============================================================
print("📊 지표 사전 계산 중... (이 단계에서 속도가 결정됩니다)")

# 모든 종목을 그룹화하여 지표 계산 (이름을 소문자로 통일)
df['ma5']   = df.groupby('symbol')['close'].transform(lambda x: x.rolling(5).mean())
df['ma20']  = df.groupby('symbol')['close'].transform(lambda x: x.rolling(20).mean())
df['ma60']  = df.groupby('symbol')['close'].transform(lambda x: x.rolling(60).mean())

# 표준편차 및 볼린저 밴드 기초 값
df['std20'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(20).std())
df['bb_upper'] = df['ma20'] + (2 * df['std20'])

# 변동성 돌파용 이전 데이터
df['high_prev'] = df.groupby('symbol')['high'].shift(1)
df['low_prev']  = df.groupby('symbol')['low'].shift(1)
df['v_ma20']    = df.groupby('symbol')['volume'].transform(lambda x: x.rolling(20).mean())

# 빈 데이터(NaN) 제거 - 지표 계산이 안 된 초기 행 삭제 (중요!)
df = df.dropna()


print("✅ 지표 생성 완료. 백테스트를 시작합니다.")

# ============================================================
# 백테스트 엔진 (동일)
# ============================================================
def run_backtest(strategy_class):
    all_returns = []
    # symbol별 루프 돌 때 인덱스 초기화 추가
    for sym in df["symbol"].unique():
        sub = df[df["symbol"] == sym].copy().reset_index(drop=True) 
        if len(sub) < 50: continue
        
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
                    exit_price = row["close"]
                    all_returns.append((exit_price - position["entry_price"]) / position["entry_price"])
                    position = None
    return pd.Series(all_returns)

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

# 실행
# [파일 맨 하단 실행 섹션]
rA = run_backtest(VolatilityBreakout_A)
rB = run_backtest(VolatilityBreakout_B)
rC = run_backtest(VolatilityBreakout_C)  # rB -> rC로 수정 완료

print_result("A (추세확정형)", rA)
print_result("B (신고가갱신형)", rB)
print_result("C (초단기 신고가 반응형)", rC) # rB -> rC로 수정 완료

