import sys
import os
import pandas as pd
import numpy as np

# [IRONCLAD V27] 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from strategy import (
    MeanReversionBBStrategy_A,
    MeanReversionBBStrategy_B,
    MeanReversionBBStrategy_C,
    MeanReversion_Disparity
)

# 1. 데이터 로드 및 전처리
data_path = r"data/merged.csv"
if not os.path.exists(data_path):
    print(f"❌ 에러: {data_path} 파일을 찾을 수 없습니다.")
    sys.exit()

df = pd.read_csv(data_path)
df.columns = [c.lower() for c in df.columns]

# --- [날짜 보정] 숫자형 타임스탬프 처리 ---
date_col = next((c for c in df.columns if c in ['datetime', 'timestamp', 'date']), None)
if date_col:
    # unit='ms' 또는 's'를 명시하거나, 형식이 깨졌을 경우 자동 추정
    try:
        df['datetime'] = pd.to_datetime(df[date_col])
        if df['datetime'].dt.year.min() <= 1970: # 1970년으로 나오면 단위 오류일 가능성 높음
             df['datetime'] = pd.to_datetime(df[date_col], unit='ms') # 밀리초 단위 시도
    except:
        df['datetime'] = pd.to_datetime(df[date_col], errors='coerce')
else:
    print("❌ 에러: 날짜 관련 컬럼이 없습니다.")
    sys.exit()

df = df.sort_values(['symbol', 'datetime']).reset_index(drop=True)

# 2. 지표 계산 (bb_middle 추가)
def prepare_indicators(df):
    print("📊 지표 계산 중 (bb_middle 포함)...")
    # 필수 지표: 볼린저 밴드
    df['ma20'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(20).mean())
    df['std20'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(20).std())
    df['bb_lower'] = df['ma20'] - (2 * df['std20'])
    df['bb_middle'] = df['ma20']  # <--- 에러 해결: strategy.py에서 요구하는 컬럼
    
    # 추가 지표: 거래량 및 RSI
    df['volume_ma'] = df.groupby('symbol')['volume'].transform(lambda x: x.rolling(20).mean())
    df['volume_ratio'] = df['volume'] / (df['volume_ma'] + 1e-9)
    
    delta = df.groupby('symbol')['close'].diff()
    gain = delta.where(delta > 0, 0).groupby(df['symbol']).transform(lambda x: x.rolling(14).mean())
    loss = (-delta.where(delta < 0, 0)).groupby(df['symbol']).transform(lambda x: x.rolling(14).mean())
    df['rsi'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))
    
    return df.dropna().copy()

df = prepare_indicators(df)

# 3. 백테스트 함수
def run_backtest(strategy_class, target_df):
    results = []
    for sym in target_df["symbol"].unique():
        sub = target_df[target_df["symbol"] == sym].copy().reset_index(drop=True)
        if len(sub) < 50: continue
        strategy = strategy_class()
        position = None
        for i in range(len(sub)):
            row = sub.iloc[i]
            if position is None:
                if strategy.on_bar(row, position) == "BUY":
                    position = {"entry_price": row["close"], "hold_bars": 0}
            else:
                # position 딕셔너리에 hold_bars 정보 업데이트 (전략 요구사항 대응)
                position["hold_bars"] += 1
                if strategy.on_position(row, position) == "EXIT":
                    pnl = (row["close"] - position["entry_price"]) / position["entry_price"]
                    results.append(pnl)
                    position = None
    return pd.Series(results)

def analyze(r):
    if len(r) == 0: return "거래 없음"
    win_rate = (r > 0).mean()
    loss_sum = abs(r[r < 0].sum())
    pf = r[r > 0].sum() / loss_sum if loss_sum != 0 else float('inf')
    return f"승률:{win_rate:.2%} | PF:{pf:.2f} | 건수:{len(r)}"

# 4. 실행부
if __name__ == "__main__":
    n = len(df)
    split_idx = int(n * 0.7)
    df_is = df.iloc[:split_idx]
    df_oos = df.iloc[split_idx:]

    print(f"📅 데이터 총 개수: {n:,}행")
    print(f"📅 학습 구간(IS): {df_is['datetime'].min()} ~ {df_is['datetime'].max()}")
    print(f"📅 검증 구간(OOS): {df_oos['datetime'].min()} ~ {df_oos['datetime'].max()}")
    print("-" * 60)

    strategies = [
        ("Strategy_A", MeanReversionBBStrategy_A),
        ("Strategy_B", MeanReversionBBStrategy_B),
        ("Strategy_C", MeanReversionBBStrategy_C),
        ("Disparity", MeanReversion_Disparity)
    ]

    for name, cls in strategies:
        res_is = run_backtest(cls, df_is)
        res_oos = run_backtest(cls, df_oos)
        
        print(f"[{name}]")
        print(f"  In-Sample (학습): {analyze(res_is)}")
        print(f"  Out-of-Sample(검증): {analyze(res_oos)}")
        
        if len(res_is) > 5 and len(res_oos) > 0:
            is_pf = res_is[res_is > 0].sum() / abs(res_is[res_is < 0].sum()) if res_is[res_is < 0].sum() != 0 else 1.0
            oos_pf = res_oos[res_oos > 0].sum() / abs(res_oos[res_oos < 0].sum()) if res_oos[res_oos < 0].sum() != 0 else 1.0
            
            if oos_pf < 1.0:
                print("  ⚠️ 과적합 의심 (검증 구간 손실)")
            elif oos_pf < is_pf * 0.6:
                print("  ⚠️ 주의: 성능 하락폭 큼")
            else:
                print("  ✅ 통과: 강건한 전략")
        print("-" * 60)