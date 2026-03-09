# order_manager.py
import sys

def safe_halt(reason: str):
    print(f"[SAFE_HALT][ORDER_MANAGER] {reason}")
    sys.exit(1)

def _require(data, key):
    if key not in data or data[key] is None:
        safe_halt(f"MISSING_REQUIRED_KEY: {key}")
    return data[key]

def execute_order(intent, exchange, strategy_spec):
    allowed_types = _require(strategy_spec, "allowed_order_types")
    order_type = _require(intent, "order_type")
    
    if order_type not in allowed_types:
        safe_halt(f"INVALID_ORDER_TYPE: {order_type}")

    symbol = _require(intent, "symbol")
    side = _require(intent, "side")
    size = _require(intent, "size")

    order_res = None
    try:
        if order_type == "market":
            order_res = exchange.market_order(symbol=symbol, side=side, size=size)
        elif order_type == "limit":
            price = _require(intent, "price")
            order_res = exchange.limit_order(symbol=symbol, side=side, size=size, price=price)
        else:
            # allowed_types 검증을 통과했으나 분기가 없는 경우 (구조적 결함)
            safe_halt(f"LOGIC_GAP_IN_ORDER_TYPE: {order_type}")
            
    except Exception as e:
        safe_halt(f"EXCHANGE_API_CRITICAL_FAILURE: {str(e)}")

    # 4. API 응답 무결성 검증 (return 전 강제 확인)
    if order_res is None or "uuid" not in order_res:
        safe_halt("ORDER_EXECUTION_FAILED: Missing response or uuid")

    return order_res