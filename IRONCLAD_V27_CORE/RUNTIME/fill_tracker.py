# fill_tracker.py
import sys

def safe_halt(reason: str):
    print(f"[SAFE_HALT][FILL_TRACKER] {reason}")
    sys.exit(1)

def track_fill(order_id, exchange):
    status = exchange.get_order(order_id)
    
    if "state" not in status:
        safe_halt("ORDER_STATUS_KEY_MISSING: state")

    state = status["state"]

    # TRINITY 상태 매핑
    mapping = {
        "done": "FILLED",
        "wait": "OPEN",
        "watch": "OPEN",
        "cancel": "CANCELLED"
    }

    if state not in mapping:
        safe_halt(f"UNKNOWN_ORDER_STATE: {state}")

    return mapping[state]