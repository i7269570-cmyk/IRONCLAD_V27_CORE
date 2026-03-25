import sys
import os
import pandas as pd

# 🔥 IRONCLAD 경로 연결 (run.py 있는 위치)
IRONCLAD_PATH = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V30\RUNTIME"
sys.path.append(IRONCLAD_PATH)

from run import IroncladEngine

# 종목
SYMBOL = "000660"

file_path = f"data/processed/stock/{SYMBOL}/data.csv"

df = pd.read_csv(file_path)

engine = IroncladEngine()

print("=== REPLAY START ===")

for i in range(100, len(df)):

    row = df.iloc[i].to_dict()

    try:
        result = engine.run_cycle(row)

        if result:
            print(f"[{row['date']} {row['time']}] SIGNAL:", result)

    except Exception as e:
        print("ERROR:", e)
        break

print("=== END ===")