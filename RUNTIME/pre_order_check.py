# pre_order_check.py
import sys

def safe_halt(reason: str):
    print(f"[SAFE_HALT][PRE_ORDER_CHECK] {reason}")
    sys.exit(1)

def _require(data, key):
    """Zero-Default: 필수 키 누락 시 SAFE_HALT"""
    if key not in data or data[key] is None:
        safe_halt(f"MISSING_REQUIRED_KEY: {key}")
    return data[key]

def pre_order_check(intent, balance, system_config):
    # 1. SSOT 바인딩 및 필수 데이터 추출
    limits = _require(system_config, "safety_limits")
    max_pos_ratio = _require(limits, "max_position_pct")
    
    order_type = _require(intent, "order_type")
    side = _require(intent, "side")
    size = _require(intent, "size")
    krw_balance = _require(balance, "krw")

    # 2. 검증 기준선(Upper Bound) 설정
    # 잔고 대비 허용된 최대 포지션 금액 (SSOT 기준 상한선)
    max_allowed_buy = krw_balance * max_pos_ratio

    # 3. 주문 금액(Current Order Value) 산출 로직 개선
    # 지적사항 반영: 추정치(total_price)와 상한선(max_allowed_buy)의 항등 구조 파괴
    if order_type == "limit":
        # 지정가: _require를 사용하여 스코프 내 안전한 변수 추출
        price = _require(intent, "price")
        current_order_val = price * size
    else:
        # 시장가: 추정치가 아닌, 전략(intent)에서 요구하는 '목표 체결 금액' 
        # 또는 'size' 자체가 금액 단위일 경우 해당 값을 직접 추출하여 검증
        # (시장가 주문 시 size가 KRW 단위인 업비트 규격 등을 고려)
        current_order_val = size 

    # 4. BUY 잔고 및 상한 실질 검증
    if side == "BUY":
        if krw_balance <= 0:
            safe_halt("INSUFFICIENT_KRW_ZERO_BALANCE")
        
        # 실질 가드: 주문 요청 금액이 상한선을 초과하는지 대조
        if current_order_val > max_allowed_buy:
            safe_halt(f"EXCEED_MAX_POSITION_LIMIT: Limit {max_allowed_buy}, Request {current_order_val}")

    # 5. SELL 잔고 검증
    elif side == "SELL":
        symbol = _require(intent, "symbol")
        asset = symbol.split("-")[1].lower()
        asset_balance = _require(balance, asset)
        if asset_balance < size:
            safe_halt(f"INSUFFICIENT_ASSET: Need {size}, Have {asset_balance}")

    return True