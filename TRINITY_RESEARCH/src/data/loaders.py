import pandas as pd

def load_processed_data(path):

    df = pd.read_csv(path)

    from cleaners import clean_data
    from validators import validate_data
    from transformers import transform_data

    df = clean_data(df)
    validate_data(df)
    df = transform_data(df)

    return df