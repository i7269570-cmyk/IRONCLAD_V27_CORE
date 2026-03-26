import os
import shutil

# 🔧 원본 폴더
SOURCE_DIR = "TRINITY_RESEARCH"

# 🔧 백업 폴더
BACKUP_DIR = "TRINITY_RESEARCH_CLEAN"

# 🔥 제외할 폴더
EXCLUDE_DIRS = ["output", "__pycache__", "raw"]

# 🔥 제외할 확장자
EXCLUDE_EXT = [".pyc"]


def should_exclude_dir(dirname):
    return dirname in EXCLUDE_DIRS


def should_exclude_file(filename):
    return any(filename.endswith(ext) for ext in EXCLUDE_EXT)


def copy_filtered(src, dst):
    for root, dirs, files in os.walk(src):

        # 제외 폴더 제거
        dirs[:] = [d for d in dirs if not should_exclude_dir(d)]

        # 대상 경로 생성
        relative_path = os.path.relpath(root, src)
        target_root = os.path.join(dst, relative_path)

        os.makedirs(target_root, exist_ok=True)

        # 파일 복사
        for file in files:
            if should_exclude_file(file):
                continue

            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_root, file)

            try:
                shutil.copy2(src_file, dst_file)
            except:
                pass


if __name__ == "__main__":

    print("📦 백업 시작...")

    # 기존 백업 삭제
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)

    # 필터링 복사
    copy_filtered(SOURCE_DIR, BACKUP_DIR)

    print("✅ 완료!")
    print(f"👉 백업 폴더: {BACKUP_DIR}")