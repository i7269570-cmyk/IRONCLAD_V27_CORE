import requests
import pandas as pd
import time
import os
import urllib3

urllib3.disable_warnings()

APP_KEY = "PSFBKxCSDcCNu71O8YguohrmduY5WNrLObSu"
APP_SECRET = "NW69awZmzWBGPBhnhFbrPrJKnuhYIGCx"

BASE_URL = "https://openapi.ls-sec.co.kr:8080"

# =========================
# 토큰
# =========================
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

    data = res.json()

    if "access_token" not in data:
        raise Exception("토큰 실패:", data)

    return data["access_token"]


# =========================
# 종목 리스트 (345개)
# =========================
def get_symbols():
    path = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\output\symbols.csv"

    df = pd.read_csv(path, dtype=str)

    symbols = df["symbol"].str.zfill(6).tolist()

    print("전체 종목:", len(symbols))

    return symbols


# =========================
# 개별 조회
# =========================
def get_stock_info(token, symbol):
    url = f"{BASE_URL}/stock/market-data"

    headers = {
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
        "tr_cd": "t1101",
        "tr_cont": "N",
        "tr_cont_key": ""
    }

    body = {
        "t1101InBlock": {
            "shcode": symbol
        }
    }

    try:
        res = requests.post(url, headers=headers, json=body, verify=False)

        data = res.json()

        item = data.get("t1101OutBlock", {})

        if not item:
            print("데이터 없음:", symbol)
            return None

        price = float(item.get("price", 0))
        volume = float(item.get("volume", 0))

        if price == 0:
            return None

        return {
            "symbol": symbol,
            "price": price,
            "value": price * volume,
            "change_rate": float(item.get("diff", 0))
        }

    except Exception as e:
        print("에러:", symbol, e)
        return None


# =========================
# 상위 종목 생성
# =========================
def get_top_300(token):
    symbols = get_symbols()

    all_data = []

    for i, sym in enumerate(symbols):
        info = get_stock_info(token, sym)

        if info:
            all_data.append(info)
        else:
            print("스킵:", sym)

        if i % 20 == 0:
            print("진행:", i, "현재 수집:", len(all_data))

        time.sleep(0.2)

    print("수집 완료:", len(all_data))

    df = pd.DataFrame(all_data)

    df = df.drop_duplicates(subset=["symbol"])

    df = df.sort_values(by="value", ascending=False)

    return df.head(300)


# =========================
# 저장
# =========================
def save_csv(df):
    path = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\output\ls_top_300.csv"

    df.to_csv(path, index=False)

    print("최종 저장:", len(df))


# =========================
# 실행
# =========================
if __name__ == "__main__":
    token = get_access_token()
    df = get_top_300(token)
    save_csv(df)