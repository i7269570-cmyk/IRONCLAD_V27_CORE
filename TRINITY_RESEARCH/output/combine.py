import pandas as pd

# =========================
# 1. 데이터 불러오기
# =========================
a = pd.read_csv("ls_mean_reversion/trades.csv")
b = pd.read_csv("ls_momentum_volume/trades.csv")

# =========================
# 2. 자금 배분 적용
# =========================
a["weighted"] = a["pnl"] * 0.7
b["weighted"] = b["pnl"] * 0.3

# =========================
# 3. 길이 맞추기
# =========================
min_len = min(len(a), len(b))

a = a.iloc[:min_len]
b = b.iloc[:min_len]

# =========================
# 4. 합산
# =========================
total = a["weighted"] + b["weighted"]

# =========================
# 5. 성과 계산
# =========================
total_profit = total.sum()
avg_profit = total.mean()

# =========================
# 6. MDD 계산
# =========================
cum = total.cumsum()
drawdown = cum - cum.cummax()
mdd = drawdown.min()

# =========================
# 7. 출력
# =========================
print("========== 결과 ==========")
print("총 수익:", total_profit)
print("평균 수익:", avg_profit)
print("MDD:", mdd)
print("==========================")