import os
import pandas as pd

data_path = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\data\daily"
output_path = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\data\processed"

os.makedirs(output_path, exist_ok=True)


def make_features(df):

    # ===== 가격 =====
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df["open"] = pd.to_numeric(df["open"], errors="coerce")
    df["high"] = pd.to_numeric(df["high"], errors="coerce")
    df["low"] = pd.to_numeric(df["low"], errors="coerce")

    # ===== 거래량 (안정 처리) =====
    if "jdiff_vol" in df.columns:
        df["volume"] = pd.to_numeric(df["jdiff_vol"], errors="coerce")
    elif "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    else:
        return None

    # ===== 지표 계산 =====

    # MA20
    df["ma20"] = df["close"].rolling(20).mean()

    # RSI
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # Bollinger
    ma20 = df["close"].rolling(20).mean()
    std = df["close"].rolling(20).std()

    df["bb_middle"] = ma20
    df["bb_upper"] = ma20 + (std * 2)
    df["bb_lower"] = ma20 - (std * 2)

    # ===== 🔥 핵심: shift (미래 데이터 제거) =====
    df["ma20"] = df["ma20"].shift(1)
    df["rsi"] = df["rsi"].shift(1)
    df["bb_middle"] = df["bb_middle"].shift(1)
    df["bb_upper"] = df["bb_upper"].shift(1)
    df["bb_lower"] = df["bb_lower"].shift(1)

    # ===== 기타 feature =====
    df["avg_volume"] = df["volume"].rolling(20).mean()
    df["volume_ratio"] = df["volume"] / df["avg_volume"]

    df["previous_high"] = df["high"].rolling(20).max().shift(1)

    df["body"] = abs(df["close"] - df["open"])
    df["range"] = df["high"] - df["low"]
    df["body_ratio"] = df["body"] / df["range"].replace(0, 1)

    df["is_breakout"] = df["close"] > df["previous_high"]

    # ===== 마지막에 dropna =====
    df = df.dropna()

    return df


# =========================
# 실행 부분
# =========================

for file in os.listdir(data_path):

    if not file.endswith(".csv"):
        continue

    path = os.path.join(data_path, file)

    try:
        df = pd.read_csv(path)

        df = make_features(df)

        if df is None or len(df) == 0:
            continue

        symbol = file.replace(".csv", "")
        df["symbol"] = symbol

        save_path = os.path.join(output_path, file)
        df.to_csv(save_path, index=False)

        print("완료:", symbol)

    except Exception as e:
        print("에러:", file, e)