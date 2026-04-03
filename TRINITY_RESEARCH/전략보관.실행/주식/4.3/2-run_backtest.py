import sys
import os
import pandas as pd
import numpy as np

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

# 1. 데이터 로드 및 시계열 정렬
data_path = r"data/merged.csv"
df = pd.read_csv(data_path)
df.columns = [c.lower() for c in df.columns]
df['datetime'] = pd.to_datetime(df.get('datetime', df.get('timestamp')))
df = df.sort_values(['symbol', 'datetime']).reset_index(drop=True)

# 2. 지표 계산 (전체 데이터에 대해 미리 수행)
def prepare_indicators(df):
    print("📊 지표 생성 중...")
    # 보정: groupby를 사용하여 심볼별로 계산
    df['ma20'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(20).mean())
    df['std20'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(20).std())
    df['bb_lower'] = df['ma20'] - (2 * df['std20'])
    df['volume_ma'] = df.groupby('symbol')['volume'].transform(lambda x: x.rolling(20).mean())
    
    # RSI
    delta = df.groupby('symbol')['close'].diff()
    gain = delta.where(delta > 0, 0).groupby(df['symbol']).transform(lambda x: x.rolling(14).mean())
    loss = (-delta.where(delta < 0, 0)).groupby(df['symbol']).transform(lambda x: x.rolling(14).mean())
    df['rsi'] = 100 - (100 / (1 + (gain / loss)))
    return df.dropna()

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
                    position = {"entry_price": row["close"]}
            else:
                if strategy.on_position(row, position) == "EXIT":
                    pnl = (row["close"] - position["entry_price"]) / position["entry_price"]
                    results.append(pnl)
                    position = None
    return pd.Series(results)

def analyze(name, r):
    if len(r) == 0: return "N/A"
    win_rate = (r > 0).mean()
    pf = r[r > 0].sum() / abs(r[r < 0].sum()) if r[r < 0].sum() != 0 else float('inf')
    return f"승률:{win_rate:.2%} | PF:{pf:.2f} | 건수:{len(r)}"

# 4. 과적합 검증 실행 (In-Sample vs Out-of-Sample)
if __name__ == "__main__":
    # 데이터를 시간순으로 정렬했으므로 비율로 나눔
    unique_dates = sorted(df['datetime'].unique())
    n = len(unique_dates)
    
    # 70%는 전략 최적화용(IS), 30%는 미지의 데이터 검증용(OOS)
    split_idx = int(n * 0.7)
    is_date = unique_dates[split_idx]
    
    df_is = df[df['datetime'] < is_date]
    df_oos = df[df['datetime'] >= is_date]
    
    print(f"📅 학습 기간(IS): {unique_dates[0]} ~ {unique_dates[split_idx-1]}")
    print(f"📅 검증 기간(OOS): {unique_dates[split_idx]} ~ {unique_dates[-1]}")
    print("-" * 50)

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
        print(f"  In-Sample (학습): {analyze(name, res_is)}")
        print(f"  Out-of-Sample(검증): {analyze(name, res_oos)}")
        
        # 과적합 판별 로직
        if len(res_is) > 0 and len(res_oos) > 0:
            is_pf = res_is[res_is > 0].sum() / abs(res_is[res_is < 0].sum()) if res_is[res_is < 0].sum() != 0 else 2.0
            oos_pf = res_oos[res_oos > 0].sum() / abs(res_oos[res_oos < 0].sum()) if res_oos[res_oos < 0].sum() != 0 else 2.0
            
            if oos_pf < 1.0:
                print("  ⚠️ 경고: 과적합 의심 (검증 구간 수익성 낮음)")
            elif oos_pf < is_pf * 0.5:
                print("  ⚠️ 경고: 성능 하락폭이 큼 (파라미터 조정 필요)")
            else:
                print("  ✅ 통과: 강건한 전략 가능성 높음")
        print("-" * 50)