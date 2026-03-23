# preflight_gate.py
import os
import sys

def safe_halt(reason: str):
    """시스템 즉각 중단: 외부 예외 포획 방지를 위한 표준 출력 및 종료"""
    print(f"[SAFE_HALT] {reason}")
    sys.exit(1)

def check_existence(file_path: str):
    """파일 존재 여부 확인 (Pre-check 로직 분리)"""
    if not os.path.exists(file_path):
        safe_halt(f"Preflight Failure: File not found -> {file_path}")

def preflight_gate(config_files: list, schema_files: list):
    """지적사항 반영: 구조적 중첩 제거 및 명시적 존재 확인 수행"""
    # 1. Configuration Files Existence Check
    for config in config_files:
        check_existence(config)
            
    # 2. Schema Files Existence Check
    for schema in schema_files:
        check_existence(schema)