import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger("IRONCLAD_RUNTIME.LEDGER_WRITER")

def record_to_ledger(fills: List[Dict[str, Any]], evidence_path: str):
    """[FIX] incident 하위 오염 방지: 독립적인 ledger 디렉터리 강제 생성"""
    if not fills:
        return

    # 오염 방지를 위해 전달된 경로 하위에 전용 디렉터리 생성
    # evidence_path가 incident일 경우 incident/ledger에 기록됨으로써 상위와 분리
    target_dir = os.path.join(evidence_path, "ledger_logs")
    
    try:
        os.makedirs(target_dir, exist_ok=True)
        log_path = os.path.join(target_dir, f"ledger_{datetime.now().strftime('%Y%m%d')}.jsonl")
        
        with open(log_path, "a", encoding="utf-8") as f:
            for fill in fills:
                f.write(json.dumps({"at": datetime.now().isoformat(), "data": fill}) + "\n")
    except Exception as e:
        raise RuntimeError(f"LEDGER_WRITE_FAILURE: {str(e)}")