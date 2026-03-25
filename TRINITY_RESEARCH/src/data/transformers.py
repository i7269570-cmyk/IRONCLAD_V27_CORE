import pandas as pd

def add_features(df):

    # 평균 거래량
    df["avg_volume"] = df["volume"].rolling(20).mean()

    # 거래량 배수
    df["volume_ratio"] = df["volume"] / df["avg_volume"]

    # 이전 고가
    df["previous_high"] = df["high"].shift(1)

    # 캔들 강도
    df["body"] = df["close"] - df["open"]
    df["range"] = df["high"] - df["low"]

    df["body_ratio"] = df["body"] / df["range"]

    # 돌파 여부
    df["is_breakout"] = df["high"] > df["previous_high"]

    df = df.dropna()

    return df