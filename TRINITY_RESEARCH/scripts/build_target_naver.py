import requests
import pandas as pd

url = "https://finance.naver.com/sise/sise_quant.naver"

symbols = []

for page in range(1, 5):  # 1~4페이지 → 약 200개
    res = requests.get(f"{url}?page={page}")
    tables = pd.read_html(res.text)

    df = tables[1]

    df = df.dropna()
    codes = df["종목코드"].astype(str).str.zfill(6)

    symbols.extend(codes.tolist())

df_out = pd.DataFrame({"symbol": symbols})
df_out.to_csv("output/target_200.csv", index=False)

print("완료:", len(df_out))