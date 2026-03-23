# integrity_guard.py
import hashlib
import sys
from pathlib import Path

def safe_halt(reason: str):
    print(f"[SAFE_HALT] {reason}")
    sys.exit(1)

class IntegrityGuard:
    def __init__(self, target_path: str, expected_hash: str):
        """지적사항 반영: __init__ 내 자동 check() 호출 로직 제거"""
        self.target_path = Path(target_path)
        self.expected_hash = expected_hash

    def check(self):
        """바이너리 해싱(rb)을 통한 물리적 무결성 검증 수행"""
        if not self.target_path.exists():
            safe_halt(f"Integrity Violation: File missing -> {self.target_path}")
            
        try:
            with self.target_path.open("rb") as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()
            
            if current_hash != self.expected_hash:
                safe_halt(f"Integrity Violation: Hash mismatch for {self.target_path}")
                
            print(f"[INTEGRITY_PASS] {self.target_path.name}")
        except Exception as e:
            safe_halt(f"Integrity Check Error: {str(e)}")