import os
import hashlib

class IntegrityGuard:
    def __init__(self, locked_path: str):
        self.locked_path = locked_path
        self.targets = ["system_config.yaml", "schema.json", "recovery_policy.yaml"]
        self.baseline_hashes = {f: self._calc_hash(os.path.join(locked_path, f)) for f in self.targets}

    def _calc_hash(self, path: str) -> str:
        sha = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192): sha.update(chunk)
        return sha.hexdigest()

    def check(self) -> bool:
        """변조 감지 시 raise 수행"""
        for f in self.targets:
            if self._calc_hash(os.path.join(self.locked_path, f)) != self.baseline_hashes[f]:
                raise RuntimeError(f"INTEGRITY_FAIL: {f} modified")
        return True