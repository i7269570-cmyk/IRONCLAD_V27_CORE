import pandas as pd
import os

strategies = {
    "ls_momentum_volume": "output/ls_momentum_volume/trades.csv",
    "ls_mean_reversion": "output/ls_mean_reversion/trades.csv"
}

for name, path in strategies.items():
    if not os.path.exists(path):
        print(f"❌ {name}: 파일 없음")
        continue

    if os.path.getsize(path) == 0:
        print(f"❌ {name}: 거래 없음 (파일 비어있음)")
        continue

    df = pd.read_csv(path)

    if df.empty:
        print(f"❌ {name}: 거래 없음")
        continue

    print(f"\n===== {name.upper()} =====")
    print("총 거래수:", len(df))
    print("승률:", round((df["pnl"] > 0).mean(), 3))
    print("PF:", round(df[df["pnl"] > 0]["pnl"].sum() / abs(df[df["pnl"] < 0]["pnl"].sum()) if len(df[df["pnl"] < 0]) > 0 else float('inf'), 3))
    print("최대 손실:", round(df["pnl"].min(), 4))
    print("평균 수익:", round(df["pnl"].mean(), 6))
    print("-" * 60)