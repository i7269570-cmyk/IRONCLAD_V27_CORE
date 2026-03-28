import pandas as pd
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.join(base_dir, "..", "data")

files = os.listdir(data_path)

all_returns = []


def run_strategy(df):
    trades = []

    # 컬럼 정리
    if "close" not in df.columns:
        if "Close" in df.columns:
            df["close"] = df["Close"]
        else:
            return trades

    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    # 변화율
    df["change"] = df["close"].pct_change()

    for i in range(5, len(df) - 1):
        row = df.iloc[i]

        # ⭐ 조건 (확실히 거래 나오게)
        if row["change"] < -0.002:  # -0.2%
            entry = df.iloc[i]["close"]
            exit = df.iloc[i + 1]["close"]

            if entry > 0:
                ret = (exit - entry) / entry
                trades.append(ret)

    return trades


for file in files:
    if not file.endswith(".csv"):
        continue

    path = os.path.join(data_path, file)

    try:
        df = pd.read_csv(path)

        if len(df) < 50:
            continue

        trades = run_strategy(df)

        all_returns.extend(trades)

    except Exception as e:
        print("에러:", file, e)


# =========================
# 결과
# =========================
if len(all_returns) == 0:
    print("❌ 거래 없음 → 데이터 문제")
else:
    r = pd.Series(all_returns)

    win = (r > 0).mean()
    pf = r[r > 0].sum() / abs(r[r < 0].sum())
    avg = r.mean()
    mdd = (r.cumsum().cummax() - r.cumsum()).max()

    print("\n===== RESULT =====")
    print("거래수:", len(r))
    print("승률:", round(win, 3))
    print("PF:", round(pf, 3))
    print("평균:", round(avg, 6))
    print("MDD:", round(mdd, 4))