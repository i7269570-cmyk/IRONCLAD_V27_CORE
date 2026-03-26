import os
import pandas as pd

RAW_DIR = "data/raw/stock"
PROCESSED_DIR = "data/processed/stock"

os.makedirs(PROCESSED_DIR, exist_ok=True)


def clean_stock_data(path):
    df = pd.read_csv(path)
    df = df.sort_values(["date", "time"]).reset_index(drop=True)
    return df


symbols = [s for s in os.listdir(RAW_DIR) if os.path.isdir(os.path.join(RAW_DIR, s))]

for symbol in symbols:
    symbol_path = os.path.join(RAW_DIR, symbol)
    output_symbol_path = os.path.join(PROCESSED_DIR, symbol)
    os.makedirs(output_symbol_path, exist_ok=True)

    files = [f for f in os.listdir(symbol_path) if f.endswith(".csv")]

    for file in files:
        input_path = os.path.join(symbol_path, file)
        output_path = os.path.join(output_symbol_path, file)

        df = clean_stock_data(input_path)

        # 기본 피처
        df["volume_ma"] = df["volume"].rolling(20).mean()
        df["close_prev_1"] = df["close"].shift(1)
        df["close_prev_5"] = df["close"].shift(5)
        df["high_prev_1"] = df["high"].shift(1)
        df["volume_prev_5"] = df["volume"].shift(5)

        # ORB 피처 (09:00 ~ 09:09)
        df["time_str"] = df["time"].astype(str).str.zfill(6)
        df["hhmm"] = df["time_str"].str[:4]

        orb_mask = (df["hhmm"] >= "0900") & (df["hhmm"] < "0910")

        # 날짜별 ORB High / Low 계산
        df["orb_high_10"] = df[orb_mask].groupby("date")["high"].transform("max")
        df["orb_low_10"] = df[orb_mask].groupby("date")["low"].transform("min")

        # 이후 봉까지 forward fill
        df["orb_high_10"] = df.groupby("date")["orb_high_10"].ffill()
        df["orb_low_10"] = df.groupby("date")["orb_low_10"].ffill()

        # 결측치 제거
        df = df.dropna().reset_index(drop=True)

        # 저장
        df.to_csv(output_path, index=False)

    print(f"완료: {symbol}")