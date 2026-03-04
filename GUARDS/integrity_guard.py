import hashlib
import json
import sys
import yaml

def safe_halt(reason: str):
    print(f"[SAFE_HALT] {reason}")
    sys.exit(1)

def calculate_file_hash(file_path: str) -> str:
    try:
        with open(file_path, "r") as f:
            config_data = yaml.safe_load(f)
        
        config_str = json.dumps(config_data, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    except Exception as e:
        safe_halt(f"Integrity File Access Failure: {str(e)}")

class IntegrityGuard:
    def __init__(self, target_path: str, initial_hash: str):
        try:
            self._target_path = target_path
            self._locked_hash = initial_hash
            self.check()
        except Exception as e:
            safe_halt(f"Integrity Guard Init Failure: {str(e)}")

    def check(self):
        try:
            current_hash = calculate_file_hash(self._target_path)
            
            if current_hash != self._locked_hash:
                safe_halt(f"Integrity Violation: {self._target_path} modified")
                
        except Exception as e:
            safe_halt(f"Integrity Check Runtime Failure: {str(e)}")