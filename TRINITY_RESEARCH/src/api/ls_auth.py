import requests
import time

class LSAuthManager:
    def __init__(self, app_key, app_secret):
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = None
        self.expire_time = 0

    def get_access_token(self):
        # 만료 5분 전이면 자동 갱신
        if time.time() > self.expire_time - 300:
            self._refresh_token()
        return self.access_token

    def _refresh_token(self):
        # 1. 8080 포트를 뺀 최신 OPEN API 표준 주소
        url = "https://openapi.ls-sec.co.kr/oauth2/token"
        
        # 2. 서버가 요구하는 가장 표준적인 헤더
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "charset": "utf-8"
        }
        
        # 3. 사진에서 확인한 그 32자리 시크릿이 전달되는 데이터 구조
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "scope": "oob"
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            
            # 📡 서버 응답 상태와 내용을 정밀하게 출력
            print(f"📡 서버 응답 코드: {response.status_code}")
            
            res_json = response.json()
            
            if "access_token" in res_json:
                self.access_token = res_json["access_token"]
                self.expire_time = time.time() + int(res_json.get("expires_in", 86400))
                print(f"✅ [실전] 드디어 토큰 발급 성공! 출항합니다.")
            else:
                print(f"❌ 실패 상세 원인: {res_json}")
                if response.status_code == 403:
                    print("💡 팁: 홈페이지 [API 서비스 신청] 메뉴에서 '실전투자' 신청이 '사용중'인지 꼭 확인하세요!")
                
        except Exception as e:
            print(f"🔥 통신 에러 발생: {e}")