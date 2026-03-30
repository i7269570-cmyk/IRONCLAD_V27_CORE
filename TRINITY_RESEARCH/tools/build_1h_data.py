import os
import pandas as pd

RAW_PATH = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\data\raw\stock"
SAVE_PATH = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\data\raw\stock_1h"

os.makedirs(SAVE_PATH, exist_ok=True)

files = [f for f in os.listdir(RAW_PATH) if f.endswith(".csv")]

print("파일 수:", len(files))

for file in files:
    path = os.path.join(RAW_PATH, file)
    symbol = file.split("_")[0]
    
    try:
       df = pd.read_csv(path)
    except:
        print("스킵 (빈 파일):", file)
        continue

    if df.empty:
        print("스킵 (데이터 없음):", file)
        continue   

    # datetime 생성
    df["datetime"] = pd.to_datetime(df["date"].astype(str) + df["time"].astype(str).str.zfill(6))

    df = df.sort_values("datetime")

    # 1시간봉 변환
    df_1h = df.set_index("datetime").resample("1H").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "jdiff_vol": "sum",
        "value": "sum"
    }).dropna()

    save_file = os.path.join(SAVE_PATH, f"{symbol}_1h.csv")
    df_1h.to_csv(save_file)

    print("완료:", symbol)