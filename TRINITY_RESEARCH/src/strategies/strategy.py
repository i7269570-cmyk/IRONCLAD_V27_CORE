import pandas as pd

# =========================
# 데이터 로드
# =========================
data_path = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\data\merged.csv"

df = pd.read_csv(data_path)
df.columns = [c.lower() for c in df.columns]

required_cols = ["close", "rsi", "bb_lower", "ma20", "low", "symbol"]
for col in required_cols:
    if col not in df.columns:
        print(f"❌ {col} 컬럼 없음")
        exit()

df = df.dropna(subset=required_cols)

# =========================
# 전략 A (현재)
# =========================
def strategy_A(row):
    try:
        if row['close'] < row['ma20'] * 0.97:
            return False

        if row['rsi'] < 45 and row['close'] <= row['bb_lower'] * 1.01:
            if row['close'] > row['low'] * 1.005:
                return True
    except:
        return False

    return False


# =========================
# 전략 B (강화)
# =========================
def strategy_B(row):
    try:
        if row['close'] < row['ma20'] * 0.98:
            return False

        if row['rsi'] < 40 and row['close'] <= row['bb_lower'] * 1.005:
            if row['close'] > row['low'] * 1.01:
                return True
    except:
        return False

    return False


# =========================
# 백테스트
# =========================
def run_backtest(strategy_func):
    returns = []

    for sym in df["symbol"].unique():
        sub = df[df["symbol"] == sym].copy()

        if len(sub) < 50:
            continue

        for i in range(20, len(sub) - 2):

            row = sub.iloc[i]

            if strategy_func(row):

                entry = sub.iloc[i + 1]["close"]
                exit_price = sub.iloc[i + 2]["close"]

                if entry > 0:
                    returns.append((exit_price - entry) / entry)

    return pd.Series(returns)


# =========================
# 결과 출력
# =========================
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


# =========================
# 실행
# =========================
rA = run_backtest(strategy_A)
rB = run_backtest(strategy_B)

print_result("전략 A (현재)", rA)
print_result("전략 B (강화)", rB)