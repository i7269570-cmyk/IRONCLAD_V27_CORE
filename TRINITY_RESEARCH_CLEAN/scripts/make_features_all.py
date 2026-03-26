import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from src.data.transformers import add_features

BASE_DIR = "data/processed/stock"

symbols = os.listdir(BASE_DIR)

for symbol in symbols:

    file_path = os.path.join(BASE_DIR, symbol, "data.csv")

    try:
        df = pd.read_csv(file_path)

        df = add_features(df)

        df.to_csv(file_path, index=False)

        print(f"완료: {symbol}")

    except Exception as e:
        print(f"실패: {symbol} → {e}")