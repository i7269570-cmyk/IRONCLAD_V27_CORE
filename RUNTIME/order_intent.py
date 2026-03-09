# order_intent.py
import sys
import hashlib
import json

def safe_halt(reason: str):
    print(f"[SAFE_HALT][ORDER_INTENT] {reason}")
    sys.exit(1)

def _require(data, key):
    if key not in data or data[key] is None:
        safe_halt(f"MISSING_REQUIRED_KEY: {key}")
    return data[key]

def build_order_intent(signal_data, strategy_spec):
    # 1. SSOT 참조: 허용 주문 타입 검증
    allowed_types = _require(strategy_spec, "allowed_order_types") # ["market", "limit"]
    order_type = _require(signal_data, "order_type")
    
    if order_type not in allowed_types:
        safe_halt(f"INVALID_ORDER_TYPE_NOT_IN_SSOT: {order_type}")

    symbol = _require(signal_data, "symbol")
    side = _require(signal_data, "side")
    size = _require(signal_data, "size")
    timestamp = _require(signal_data, "timestamp")

    # 2. 지정가 주문 시 가격 필수 체크
    price = None
    if order_type == "limit":
        price = _require(signal_data, "price")

    # 3. Idempotency Key 생성 (중복 실행 차단)
    payload = {"symbol": symbol, "side": side, "size": size, "timestamp": timestamp}
    dump = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    intent_id = hashlib.sha256(dump.encode("utf-8")).hexdigest()

    return {
        "intent_id": intent_id,
        "symbol": symbol,
        "side": side,
        "size": size,
        "order_type": order_type,
        "price": price,
        "timestamp": timestamp
    }