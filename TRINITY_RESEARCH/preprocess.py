import pandas as pd
import numpy as np
import os
import glob

def calculate_indicators(df):
    try:
        # 1. 이동평균선 (기존에 없을 경우에만 새로 계산)
        if 'ma5' not in df.columns:
            df['ma5'] = df['close'].rolling(window=5).mean()
        if 'ma20' not in df.columns:
            df['ma20'] = df['close'].rolling(window=20).mean()
        
        # 2. RSI (과매도 확인용)
        if 'rsi' not in df.columns:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            # 0으로 나누기 방지
            rs = gain / loss.replace(0, np.nan)
            df['rsi'] = 100 - (100 / (1 + rs))
        
        # 3. 볼린저 밴드 (변동성 및 하단 확인용)
        if 'bb_lower' not in df.columns:
            stddev = df['close'].rolling(window=20).std()
            ma20 = df['close'].rolling(window=20).mean()
            df['bb_middle'] = ma20
            df['bb_lower'] = ma20 - (stddev * 2)
            df['bb_upper'] = ma20 + (stddev * 2)
        
        # 4. 이전 봉 데이터 (골든크로스 등 조건 비교용 필권 데이터)
        if 'ma5_prev' not in df.columns:
            df['ma5_prev'] = df['ma5'].shift(1)
        if 'ma20_prev' not in df.columns:
            df['ma20_prev'] = df['ma20'].shift(1)
            
        # 데이터 결손(NaN) 제거하여 SAFE_HALT 방지
        return df.dropna()
    except Exception as e:
        print(f"❌ 계산 중 오류 발생: {e}")
        return df

# 실행 경로 설정
DATA_PATH = "data/processed/stock"

print("🚀 지표 추가 공장 가동 시작...")

for folder in os.listdir(DATA_PATH):
    symbol_path = os.path.join(DATA_PATH, folder)
    if os.path.isdir(symbol_path):
        for file in glob.glob(os.path.join(symbol_path, "*.csv")):
            try:
                df = pd.read_csv(file)
                # 기존 데이터 보존하며 부족한 것만 추가
                df = calculate_indicators(df)
                # 동일 파일에 덮어쓰기 (SSOT 유지)
                df.to_csv(file, index=False)
                print(f"✅ {os.path.basename(file)}: 지표 업데이트 완료")
            except Exception as e:
                print(f"⚠️ {file} 처리 중 오류: {e}")

print("✨ 모든 데이터 가공이 완료되었습니다.")