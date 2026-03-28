import requests
import pandas as pd
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


def get_top_volume(token):
    url = f"{BASE_URL}/stock/market-data"

    headers = {
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
        "tr_cd": "t1452",
        "tr_cont": "N",
        "tr_cont_key": ""
    }

    body = {
        "t1452InBlock": {
            "gubun": "0",   # 전체 시장
            "jnilgubun": "1",
            "edate": "",
            "idx": 0
        }
    }

    res = requests.post(url, headers=headers, json=body, verify=False)
    data = res.json()
    
    print("DEBUG RAW:", data)  

    return data.get("t1452OutBlock1", [])


def save_target(data):
    df = pd.DataFrame(data)
    
    print("컬럼 확인:", df.columns) 

    # 컬럼 정리
    df = df.rename(columns={
        "shcode": "symbol",
        "price": "price",
        "value": "value",
        "diff": "change_rate"
    })

    df = df[["symbol", "price", "value", "change_rate"]]

    df["symbol"] = df["symbol"].astype(str).str.zfill(6)

    df = df.sort_values(by="value", ascending=False)

    # 상위 200개
    df = df.head(200)

    path = "output/target_200.csv"
    df.to_csv(path, index=False)

    print("저장 완료:", path, len(df))


if __name__ == "__main__":
    token = get_token()
    data = get_top_volume(token)
    save_target(data)