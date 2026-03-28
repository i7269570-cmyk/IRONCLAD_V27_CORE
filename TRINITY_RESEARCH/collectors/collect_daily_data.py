import requests
import pandas as pd
import time
import os
import urllib3

urllib3.disable_warnings()

APP_KEY = "PSFBKxCSDcCNu71O8YguohrmduY5WNrLObSu".strip()
APP_SECRET = "NW69awZmzWBGPBhnhFbrPrJKnuhYIGCx".strip()

BASE_URL = "https://openapi.ls-sec.co.kr:8080"

def get_access_token():
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


def get_symbols():
    df = pd.read_csv(
        r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\output\ls_top_300.csv",
        dtype=str
    )
    return df["symbol"].str.zfill(6).tolist()


def get_daily(token, symbol):
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
            "dwmcode": 1,
            "date": "",
            "idx": 0,
            "cnt": 500
        }
    }

    res = requests.post(url, headers=headers, json=body, verify=False)

    data = res.json()
    print("DEBUG:", data)

    return data.get("t1305OutBlock1", [])


def save(symbol, items):
    if not items:
        print("데이터 없음:", symbol)
        return

    import pandas as pd
    import os

    df = pd.DataFrame(items)

    # ⭐ 절대경로 강제
    path = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\data\daily"

    os.makedirs(path, exist_ok=True)

    file_path = os.path.join(path, f"{symbol}.csv")

    df.to_csv(file_path, index=False)

    print("저장 완료:", file_path)


def run():
    token = get_access_token()
    symbols = get_symbols()

    print("종목 개수 확인:", len(symbols))

    for i, sym in enumerate(symbols):

        try:
            data = get_daily(token, sym)

            if not data:
                print("데이터 없음:", sym)
                continue

            save(sym, data)

            print(f"{i+1}/{len(symbols)} 완료:", sym)

            time.sleep(2.0)

        except Exception as e:
            print("에러:", sym, e)
            continue

if __name__ == "__main__":
    run()