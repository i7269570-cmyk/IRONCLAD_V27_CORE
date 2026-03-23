import os
from typing import Dict

def run_preflight_checks(paths: Dict[str, str]) -> bool:
    """필수 경로 검증. 실패 시 raise 수행"""
    mandatory = [
        (os.path.join(paths["LOCKED"], "system_config.yaml"), True),
        (paths["STATE"], False),
        (paths["STRATEGY"], False),
        (os.path.join(paths["EVIDENCE"], "incident"), False)
    ]
    for path, is_file in mandatory:
        exists = os.path.isfile(path) if is_file else os.path.isdir(path)
        if not exists:
            raise RuntimeError(f"PREFLIGHT_FAIL: Missing {path}")
    return True