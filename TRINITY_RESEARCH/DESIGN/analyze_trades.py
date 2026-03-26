import pandas as pd


def analyze(path, name):

    df = pd.read_csv(path)

    print(f"\n===== {name} =====")

    # 총 거래수
    print("총 거래수:", len(df))

    # 승률
    win_rate = (df["pnl"] > 0).mean()
    print("승률:", round(win_rate * 100, 2), "%")

    # 평균 수익 / 손실
    avg_win = df[df["pnl"] > 0]["pnl"].mean()
    avg_loss = df[df["pnl"] < 0]["pnl"].mean()

    print("평균 수익:", round(avg_win, 5))
    print("평균 손실:", round(avg_loss, 5))

    # PF
    profit = df[df["pnl"] > 0]["pnl"].sum()
    loss = abs(df[df["pnl"] < 0]["pnl"].sum())

    pf = profit / loss if loss != 0 else 0
    print("PF:", round(pf, 3))

    # 최대 연속 손실
    df["loss"] = df["pnl"] < 0
    max_loss_streak = df["loss"].astype(int).groupby(
        (df["loss"] != df["loss"].shift()).cumsum()
    ).cumsum().max()

    print("최대 연속 손실:", max_loss_streak)


# -------------------------
# 실행
# -------------------------
if __name__ == "__main__":

    analyze("output/ls_momentum_v1/trades.csv", "LS_MOMENTUM")
    analyze("output/ls_pullback_v1/trades.csv", "LS_PULLBACK")
    analyze("output/ls_orb_v1/trades.csv", "LS_ORB")