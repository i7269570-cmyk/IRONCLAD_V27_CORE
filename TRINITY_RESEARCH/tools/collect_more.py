import os
import time
import pandas as pd

# 👉 여기만 당신 기존 수집 함수로 교체
# 예: from collectors.collect_minute_data import fetch_symbol_data
def fetch_symbol_data(symbol):
    """
    기존에 45개 만들 때 썼던 함수로 교체하세요.
    반드시 아래 컬럼으로 반환되게:
    date,time,open,high,low,close,jdiff_vol,value
    """
    raise NotImplementedError("여기에 기존 수집 함수 연결")

RAW_DIR = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\data\raw\stock"
os.makedirs(RAW_DIR, exist_ok=True)

# 👉 추가할 종목 목록 파일
SYMBOLS_FILE = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\data\symbols_add.csv"

symbols = pd.read_csv(SYMBOLS_FILE, dtype=str).iloc[:,0].str.zfill(6).tolist()

existing = set([f.split("_")[0] for f in os.listdir(RAW_DIR) if f.endswith(".csv")])

todo = [s for s in symbols if s not in existing]

print("기존:", len(existing), "추가대상:", len(todo))

for i, sym in enumerate(todo):
    try:
        df = fetch_symbol_data(sym)   # ⭐ 기존 방식 연결

        if df is None or len(df) == 0:
            print("데이터 없음:", sym)
            continue

        save_path = os.path.join(RAW_DIR, f"{sym}_1m.csv")
        df.to_csv(save_path, index=False)

        print(f"완료: {sym} ({i+1}/{len(todo)})")

        time.sleep(0.2)  # 과부하 방지

    except Exception as e:
        print("에러:", sym, e)