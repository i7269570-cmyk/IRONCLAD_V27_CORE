import os
import sys

def safe_halt(reason: str):
    print(f"[SAFE_HALT] {reason}")
    sys.exit(1)

def check_existence(file_path: str):
    try:
        if not os.path.exists(file_path):
            safe_halt(f"Preflight Failure: File not found -> {file_path}")
    except Exception as e:
        safe_halt(f"Preflight Access Error: {str(e)}")

def preflight_gate(config_files: list, schema_files: list):
    try:
        # 1. Configuration Files Existence Check
        for config in config_files:
            check_existence(config)
            
        # 2. Schema Files Existence Check
        for schema in schema_files:
            check_existence(schema)
            
    except Exception as e:
        safe_halt(f"Preflight Gate Execution Failure: {str(e)}")