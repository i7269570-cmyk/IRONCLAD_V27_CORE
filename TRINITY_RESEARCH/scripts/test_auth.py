import yaml
import sys
import os

# 프로젝트 루트 경로 추가 (src를 인식하기 위함)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from src.api.ls_auth import LSAuthManager

def run_test():
    with open("config/credentials.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    ls_config = config["LS_API"]
    
    # 이 줄을 추가해서 터미널에 찍히는 값을 홈페이지 값과 대조해 보세요.
    print(f"DEBUG - APP_KEY: [{ls_config['APP_KEY']}]")
    print(f"DEBUG - APP_SECRET: [{ls_config['APP_SECRET']}]")
    
    # 1. 설정 파일 로드
    with open("config/credentials.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    ls_config = config["LS_API"]
    
    # 2. 인증 매니저 초기화
    auth = LSAuthManager(ls_config["APP_KEY"], ls_config["APP_SECRET"])
    
    print("🔐 LS증권 API 접속 시도 중...")
    
    try:
        # 3. 토큰 발급 테스트
        token = auth.get_access_token()
        
        if token:
            print(f"✅ 인증 성공!")
            print(f"🎫 Access Token: {token[:10]}... (보안상 일부 숨김)")
            print(f"⏳ 만료 예정 시간: {auth.expire_time}")
            print("\n🚀 이제 300개 종목을 긁어올 준비가 끝났습니다.")
        else:
            print("❌ 토큰 발급 실패: 응답이 비어있습니다.")
            
    except Exception as e:
        print(f"🔥 에러 발생: {e}")
        print("💡 팁: 앱키/시크릿이 정확한지, 혹은 서버 점검 시간인지 확인해 보세요.")

if __name__ == "__main__":
    run_test()