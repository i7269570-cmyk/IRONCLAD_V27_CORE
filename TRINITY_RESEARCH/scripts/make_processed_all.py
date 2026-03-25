import os
import pandas as pd

RAW_DIR = "data/raw/stock"
PROCESSED_DIR = "data/processed/stock"

os.makedirs(PROCESSED_DIR, exist_ok=True)


def clean_stock_data(path):
    df = pd.read_csv(path)
    df = df.sort_values(["date", "time"])
    return df


symbols = os.listdir(RAW_DIR)

for symbol in symbols:
    symbol_path = os.path.join(RAW_DIR, symbol)

    if not os.path.isdir(symbol_path):
        continue

    output_symbol_path = os.path.join(PROCESSED_DIR, symbol)
    os.makedirs(output_symbol_path, exist_ok=True)

    files = [f for f in os.listdir(symbol_path) if f.endswith(".csv")]

    for file in files:
        input_path = os.path.join(symbol_path, file)
        output_path = os.path.join(output_symbol_path, file)

        df = clean_stock_data(input_path)

        # 🔥 feature 생성
        df["volume_ma"] = df["volume"].rolling(20).mean()
        df["close_prev_1"] = df["close"].shift(1)
        df["close_prev_3"] = df["close"].shift(3)
        df["close_ma_20"] = df["close"].rolling(20).mean()
        df["close_prev_5"] = df["close"].shift(5)
        df["high_prev_1"] = df["high"].shift(1)
        df["volume_prev_5"] = df["volume"].shift(5)
        
        df = df.dropna()

    print(f"완료: {symbol}")