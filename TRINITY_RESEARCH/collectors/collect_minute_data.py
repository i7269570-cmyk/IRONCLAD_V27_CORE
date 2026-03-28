import requests
import pandas as pd
import time
import os
import urllib3

urllib3.disable_warnings()

APP_KEY = "PSFBKxCSDcCNu71O8YguohrmduY5WNrLObSu".strip()
APP_SECRET = "NW69awZmzWBGPBhnhFbrPrJKnuhYIGCx".strip()

BASE_URL = "https://openapi.ls-sec.co.kr:8080"

def get_token():
    url = f"{BASE_URL}/oauth2/token"

    headers = {"content-type": "application/x-www-form-urlencoded"}

    params = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecretkey": APP_SECRET,
        "scope": "oob"
    }

    res = requests.post(url, headers=headers, params=params, verify=False)

    return res.json()["access_token"]


def get_minute_day(symbol, token, date):
    url = f"{BASE_URL}/stock/market-data"

    headers = {
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
        "tr_cd": "t1305",
        "tr_cont": "N",
        "tr_cont_key": ""
    }

    body = {
        "t1305InBlock": {
            "shcode": symbol,
            "ncnt": "1",
            "qrycnt": "500",
            "sdate": date,
            "edate": date
        }
    }

    res = requests.post(url, headers=headers, json=body, verify=False)

    data = res.json()
   
    print("DEBUG:", data)
    
    return data.get("t8412OutBlock1", [])


def collect_symbol(symbol):
    token = get_token()

    all_data = []

    # 예: 최근 250일
    dates = pd.date_range(end=pd.Timestamp.today(), periods=250)

    for d in dates:
        date_str = d.strftime("%Y%m%d")

        try:
            items = get_minute_day(symbol, token, date_str)

            if items:
                all_data.extend(items)

            print(symbol, date_str)

            time.sleep(1.2)

        except Exception as e:
            print("에러:", symbol, e)

    return pd.DataFrame(all_data)


def save(symbol, new_df):
    path = r"...\data\raw\stock"
    file_path = os.path.join(path, f"{symbol}_1m.csv")

    if os.path.exists(file_path):
        old_df = pd.read_csv(file_path)
        df = pd.concat([old_df, new_df], ignore_index=True)
        df = df.drop_duplicates()
    else:
        df = new_df

    df.to_csv(file_path, index=False)

    print("저장 완료:", symbol, len(df))

if __name__ == "__main__":

    symbols = [
        "005930",
        "000660",
        "035720",
    ]

    for sym in symbols:
        df = collect_symbol(sym)
        save(sym, df)
