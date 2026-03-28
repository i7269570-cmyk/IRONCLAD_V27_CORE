import pandas as pd
import os

raw_path = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\data\processed"

all_data = []

files = os.listdir(raw_path)

print("파일 개수:", len(files))

for file in files:
    if not file.endswith(".csv"):
        continue

    symbol = file.replace(".csv", "")
    path = os.path.join(raw_path, file)

    try:
        df = pd.read_csv(path)

        # 🔥 조건 제거
        if len(df) == 0:
            print("빈 파일:", file)
            continue

        df["symbol"] = symbol

        all_data.append(df)

        print("추가:", file, "행:", len(df))

    except Exception as e:
        print("에러:", file, e)

# =========================
# 병합
# =========================
if len(all_data) == 0:
    print("❌ 병합할 데이터 없음")
else:
    merged = pd.concat(all_data, ignore_index=True)

    save_path = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH\data\merged.csv"
    merged.to_csv(save_path, index=False)

    print("완료:", len(merged))