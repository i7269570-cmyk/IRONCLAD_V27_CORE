def validate_data(df):
    if df.isnull().any().any():
        raise ValueError("NULL 존재")

    if not df["time"].is_monotonic_increasing:
        raise ValueError("시간 역순")

    return True