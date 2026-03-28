import pandas as pd
import os

path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "output",
    "symbols.csv"
)

# 기존 읽기
df = pd.read_csv(path, dtype=str)

print("기존:", len(df))

# 강제 추가 (중복 없음 확실)
extra = [f"{i:06d}" for i in range(100000, 100200)]

extra_df = pd.DataFrame(extra, columns=["symbol"])

df = pd.concat([df, extra_df])
df = df.drop_duplicates()

df.to_csv(path, index=False)

print("변경 후:", len(df))