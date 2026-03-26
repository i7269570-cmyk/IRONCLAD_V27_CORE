import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.cleaners import clean_stock_data

input_path = "data/raw/stock/005930_1m.csv"
output_path = "data/processed/stock/005930/data.csv"

df = clean_stock_data(input_path)

df.to_csv(output_path, index=False)

print("완료:", output_path)