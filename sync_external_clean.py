import shutil
import os

SRC_PATH = r"C:\Users\PC\OneDrive\바탕 화면\IRONCLAD_V27_CORE\TRINITY_RESEARCH"
DEST_PATH = r"D:\TRINITY_RESEARCH_CLEAN"

# [업데이트] 제외할 폴더와 파일 확장자를 더 명확히 정의합니다.
EXCLUDE_DIRS = ['raw', '.git', '__pycache__', '.ipynb_checkpoints']
EXCLUDE_FILES = ['__init__.py', '.DS_Store', 'desktop.ini'] # 찌꺼기 파일들 차단

def run_sync():
    print(f"🚀 외장하드({DEST_PATH}) 정예 데이터 필터링 전송 시작...")
    
    if not os.path.exists(DEST_PATH):
        os.makedirs(DEST_PATH)

    for root, dirs, files in os.walk(SRC_PATH):
        # 1. 필요 없는 폴더 제외
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        rel_path = os.path.relpath(root, SRC_PATH)
        dest_dir = os.path.join(DEST_PATH, rel_path)
        
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        for file in files:
            # 2. 필요 없는 파일 확장자나 이름 제외
            if file in EXCLUDE_FILES or file.endswith('.pyc') or file.endswith('.tmp'):
                continue
                
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_dir, file)
            
            shutil.copy2(src_file, dest_file)
            print(f"✅ 정예 보관 완료: {file}")

    print("\n✨ 찌꺼기 없이 핵심 로직만 외장하드에 저장되었습니다.")

if __name__ == "__main__":
    run_sync()