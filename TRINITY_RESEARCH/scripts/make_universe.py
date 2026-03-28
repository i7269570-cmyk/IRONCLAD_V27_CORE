import os
import pandas as pd

data_path = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\data\daily"

symbols = []

for file in os.listdir(data_path):
    if file.endswith(".csv"):
        symbol = file.replace(".csv", "")
        symbols.append(symbol)

df = pd.DataFrame({
    "symbol": symbols
})

df = df.sort_values(by="symbol")

df.to_csv("output/target_auto.csv", index=False)

print("완료:", len(df))