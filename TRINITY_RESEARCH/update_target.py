import requests
import pandas as pd
import io
import os
import time

def final_force_fetch():
    save_path = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\data\target_300.csv"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # 사람이 사용하는 크롬 브라우저로 완벽 위장
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    all_data = []
    print("🚀 네이버 보안망을 우회하여 진짜 300개를 수집합니다...")
    
    for p in [1, 2, 3]:
        # URL 뒤에 의미 없는 숫자를 붙여 '매번 새로운 요청'인 것처럼 속입니다
        url = f"https://finance.naver.com/sise/sise_quant.naver?sosok=0&page={p}&_={int(time.time())}"
        
        response = requests.get(url, headers=headers)
        # 표 데이터 추출
        df = pd.read_html(io.StringIO(response.text))[1]
        df = df.dropna(subset=['종목명'])
        
        all_data.append(df)
        print(f"📦 {p}페이지 수집 성공! 현재까지 {len(pd.concat(all_data))}개 확보")
        
        # 네이버가 눈치채지 못하게 1.5초간 쉽니다
        time.sleep(1.5)

    # 데이터 합치기 및 300개 절삭
    final = pd.concat(all_data).reset_index(drop=True).head(300)
    
    # 저장
    final.to_csv(save_path, index=False, encoding='utf-8-sig')
    print("-" * 40)
    print(f"✅ [미션 완료] 진짜 300개 종목이 {save_path}에 저장되었습니다!")

if __name__ == "__main__":
    final_force_fetch()