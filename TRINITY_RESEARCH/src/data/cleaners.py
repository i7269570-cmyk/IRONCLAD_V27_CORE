import pandas as pd

def clean_stock_data(file_path):

    df = pd.read_csv(file_path)

    # 컬럼 이름 통일
    df = df.rename(columns={
        "jdiff_vol": "volume"
    })

    # 필요한 컬럼만 선택
    df = df[[
        "date", "time",
        "open", "high", "low", "close",
        "volume", "value"
    ]]

    # 타입 정리
    df["date"] = df["date"].astype(str)
    df["time"] = df["time"].astype(str)

    numeric_cols = ["open", "high", "low", "close", "volume", "value"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    # 결측 제거
    df = df.dropna()

    # 시간 정렬
    df = df.sort_values(["date", "time"])

    # 중복 제거
    df = df.drop_duplicates(subset=["date", "time"])

    return df