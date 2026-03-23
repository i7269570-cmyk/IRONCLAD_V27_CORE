import os
import sys
import json
from datetime import datetime
from typing import Optional


def safe_halt(reason: str) -> None:
    """
    유일한 종료 지점
    """
    print(f"[SAFE_HALT] {reason}")
    sys.exit(1)


def cancel_all_orders() -> None:
    """
    모든 미체결 주문 취소 시도
    실패해도 예외를 던지지 않고 상위로 넘김
    """
    try:
        # TODO: 실제 주문 취소 로직 연결
        print("[INFO] Attempting to cancel all open orders...")
        # placeholder
    except Exception as e:
        # 실패해도 중단하지 않음
        print(f"[WARN] Cancel-All failed: {e}")


def write_incident(reason: str, incident_dir: str) -> None:
    """
    incident 기록 (반드시 기록 시도)
    """
    os.makedirs(incident_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"incident_{timestamp}.json"
    path = os.path.join(incident_dir, filename)

    data = {
        "timestamp": timestamp,
        "reason": reason,
        "action": "SAFE_HALT"
    }

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())

    except Exception as e:
        # 🔥 fallback 반드시 남김
        fallback_path = os.path.join(incident_dir, "incident_fallback.log")
        try:
            with open(fallback_path, "a", encoding="utf-8") as f:
                f.write(
                    f"{datetime.now().isoformat()} | INCIDENT_WRITE_FAIL | "
                    f"reason={reason} | error={str(e)}\n"
                )
        except Exception as fallback_error:
            print(f"[CRITICAL] Fallback logging failed: {fallback_error}")


def handle_critical_failure(reason: str, incident_dir: str) -> None:
    """
    단일 종료 경로

    순서:
    1. Cancel-All
    2. incident 기록 (fallback 포함)
    3. SAFE_HALT
    """

    print(f"[ERROR] Critical failure: {reason}")

    # 1. Cancel-All (실패해도 진행)
    cancel_all_orders()

    # 2. Incident 기록 (반드시 시도)
    write_incident(reason, incident_dir)

    # 3. 최종 종료 (유일한 sys.exit)
    safe_halt(reason)