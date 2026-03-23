"""
MORNING_BREAKOUT - 3 Strategy Variants Backtest
구조: 전일 고가 돌파 + 거래량 필터 + 오전 시간대 진입
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, time
import warnings
warnings.filterwarnings('ignore')

# ────────────────────────────────────────────
# 데이터 로드
# ────────────────────────────────────────────
def load_data(ticker="005930.KS", period="6mo", interval="1h"):
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    df.columns = [c[0].lower() if isinstance(c, tuple) else c.lower() for c in df.columns]
    df.index = pd.to_datetime(df.index)
    if df.index.tz is not None:
        df.index = df.index.tz_convert('Asia/Seoul').tz_localize(None)
    df = df[['open','high','low','close','volume']].dropna()
    return df

# ────────────────────────────────────────────
# 공통 피처 생성
# ────────────────────────────────────────────
def build_features(df):
    df = df.copy()
    df['date'] = df.index.date
    # 전일 고가
    daily_high = df.groupby('date')['high'].max().shift(1)
    df['prev_high'] = df['date'].map(daily_high)
    # 20봉 평균 거래량
    df['avg_vol_20'] = df['volume'].rolling(20).mean()
    df['hour'] = df.index.hour
    df['minute'] = df.index.minute
    return df

# ────────────────────────────────────────────
# 백테스트 엔진
# ────────────────────────────────────────────
def run_backtest(df, cfg):
    df = df.copy()
    results = []
    position = None

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i - 1]

        # ── 포지션 청산 확인 ──
        if position is not None:
            bars_held = i - position['entry_idx']
            ret = (row['close'] - position['entry_price']) / position['entry_price']
            net = ret - cfg['fee_pct']

            exit_reason = None
            if ret >= cfg['tp']:
                exit_reason = 'TP'
            elif ret <= cfg['sl']:
                exit_reason = 'SL'
            elif bars_held >= cfg['max_bars']:
                exit_reason = 'MAX_BARS'

            if exit_reason:
                results.append({
                    'entry_time': position['entry_time'],
                    'exit_time': row.name,
                    'entry_price': position['entry_price'],
                    'exit_price': row['close'],
                    'return_pct': round(net * 100, 3),
                    'bars': bars_held,
                    'reason': exit_reason
                })
                position = None
            continue  # 포지션 보유 중 신규 진입 없음

        # ── 시간 필터 ──
        t = row['hour'] * 60 + row['minute']
        t_start = cfg['time_start'][0] * 60 + cfg['time_start'][1]
        t_end   = cfg['time_end'][0]   * 60 + cfg['time_end'][1]
        if not (t_start <= t <= t_end):
            continue

        # ── 진입 조건 ──
        breakout = prev['close'] > prev['prev_high'] if pd.notna(prev['prev_high']) else False
        vol_ok   = prev['volume'] > prev['avg_vol_20'] * cfg['vol_mult']

        if breakout and vol_ok:
            # 다음 봉 시가 진입
            entry_price = row['open']
            position = {
                'entry_idx': i,
                'entry_time': row.name,
                'entry_price': entry_price,
            }

    return pd.DataFrame(results)

# ────────────────────────────────────────────
# 결과 출력
# ────────────────────────────────────────────
def print_result(name, res):
    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")
    if res.empty:
        print("  거래 없음")
        return
    wins = res[res['return_pct'] > 0]
    print(f"  총 거래 수   : {len(res)}")
    print(f"  승률         : {len(wins)/len(res)*100:.1f}%")
    print(f"  평균 수익률  : {res['return_pct'].mean():.3f}%")
    print(f"  총 수익률    : {res['return_pct'].sum():.3f}%")
    print(f"  최대 수익    : {res['return_pct'].max():.3f}%")
    print(f"  최대 손실    : {res['return_pct'].min():.3f}%")
    print(f"  청산 사유    :\n{res['reason'].value_counts().to_string()}")
    print(f"\n  최근 거래 5건:")
    print(res[['entry_time','exit_time','return_pct','reason']].tail(5).to_string(index=False))


# ────────────────────────────────────────────
#  STRATEGY_1  (약 - Weak)
# ────────────────────────────────────────────
"""
[STRATEGY_1] — WEAK
조건식:
  진입: close > prev_high AND volume > avg_vol_20 * 1.3
  시간: 09:00 ~ 10:30
  청산: TP +2% | SL -1.5% | MAX_BARS 5
  수수료: 0.15%
"""

CFG_1 = {
    'time_start': (9, 0),
    'time_end':   (10, 30),
    'vol_mult':   1.3,
    'tp':         0.02,
    'sl':        -0.015,
    'max_bars':   5,
    'fee_pct':    0.0015,
}

# ────────────────────────────────────────────
#  STRATEGY_2  (중 - Medium)  ← 원본 구조 기준
# ────────────────────────────────────────────
"""
[STRATEGY_2] — MEDIUM (원본)
조건식:
  진입: close > prev_high AND volume > avg_vol_20 * 1.5
  시간: 09:00 ~ 10:30
  청산: TP +3% | SL -2% | MAX_BARS 3
  수수료: 0.15%
"""

CFG_2 = {
    'time_start': (9, 0),
    'time_end':   (10, 30),
    'vol_mult':   1.5,
    'tp':         0.03,
    'sl':        -0.02,
    'max_bars':   3,
    'fee_pct':    0.0015,
}

# ────────────────────────────────────────────
#  STRATEGY_3  (강 - Strong)
# ────────────────────────────────────────────
"""
[STRATEGY_3] — STRONG
조건식:
  진입: close > prev_high AND volume > avg_vol_20 * 2.0
  시간: 09:00 ~ 09:50  (더 좁은 시간대)
  청산: TP +5% | SL -2.5% | MAX_BARS 2
  수수료: 0.15%
"""

CFG_3 = {
    'time_start': (9, 0),
    'time_end':   (9, 50),
    'vol_mult':   2.0,
    'tp':         0.05,
    'sl':        -0.025,
    'max_bars':   2,
    'fee_pct':    0.0015,
}

# ────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────
if __name__ == "__main__":
    TICKER = "005930.KS"   # 삼성전자. 원하는 종목으로 변경
    PERIOD = "6mo"
    INTERVAL = "1h"

    print(f"\n[데이터 로드] {TICKER} / {PERIOD} / {INTERVAL}")
    df_raw = load_data(TICKER, PERIOD, INTERVAL)
    df_feat = build_features(df_raw)
    print(f"  로드 완료: {len(df_feat)}행 ({df_feat.index[0]} ~ {df_feat.index[-1]})")

    res1 = run_backtest(df_feat, CFG_1)
    res2 = run_backtest(df_feat, CFG_2)
    res3 = run_backtest(df_feat, CFG_3)

    print_result("STRATEGY_1 — WEAK   | vol*1.3 | TP2% SL1.5% bars5", res1)
    print_result("STRATEGY_2 — MEDIUM | vol*1.5 | TP3% SL2.0% bars3", res2)
    print_result("STRATEGY_3 — STRONG | vol*2.0 | TP5% SL2.5% bars2", res3)

    # CSV 저장 (선택)
    for name, res in [("S1_weak", res1), ("S2_medium", res2), ("S3_strong", res3)]:
        if not res.empty:
            res.to_csv(f"result_{name}.csv", index=False)
            print(f"\n  result_{name}.csv 저장 완료")