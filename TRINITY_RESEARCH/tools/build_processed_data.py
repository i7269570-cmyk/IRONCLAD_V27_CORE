import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.cleaners import clean_stock_data
from src.data.transformers import add_features

raw_path = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\data\raw\stock"
save_path = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\data\processed"

os.makedirs(save_path, exist_ok=True)

files = os.listdir(raw_path)

print("파일 개수:", len(files))

for file in files:
    if not file.endswith(".csv"):
        continue

    symbol = file.split("_")[0]
    path = os.path.join(raw_path, file)

    try:
        df = clean_stock_data(path)
        df = add_features(df)

        df["symbol"] = symbol

        save_file = os.path.join(save_path, f"{symbol}.csv")
        df.to_csv(save_file, index=False)

        print("완료:", symbol)

    except Exception as e:
        print("에러:", file, e)