import os
import yaml
import logging
from typing import Dict, Any

logger = logging.getLogger("IRONCLAD_RUNTIME.RISK_GATE")

def validate_risk_and_size(asset_info: Dict[str, Any], current_state: Dict[str, Any], strategy_path: str) -> Dict[str, Any]:
    """
    [RISK 해결] 최대 한도, 자산군 중복, 전략 기반 사이징을 수행한다.
    """
    symbol = asset_info.get("symbol")
    asset_type = asset_info.get("asset_type")
    current_positions = current_state.get("positions", [])
    
    # [1] 전략 설정 로드 (하드코딩 제거)
    try:
        rules_path = os.path.join(strategy_path, "risk_rules.yaml")
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f)
        
        max_pos = rules.get("max_position_limit", 2)
        unit_size = rules.get("fixed_unit_size", 0.0) # 기본값 0으로 설정하여 설정 강제
    except Exception as e:
        raise RuntimeError(f"RISK_GATE_CONFIG_ERROR: {e}")

    # [2] 최대 포지션 수 제한 (2개)
    if len(current_positions) >= max_pos:
        logger.warning(f"RISK_GATE: Max position limit ({max_pos}) reached. Blocking {symbol}.")
        return {"allowed": False, "reason": "MAX_POS_LIMIT"}

    # [3] 동일 심볼 및 동일 자산군(asset_type) 중복 검사
    for pos in current_positions:
        if pos.get("symbol") == symbol:
            return {"allowed": False, "reason": "DUPLICATE_SYMBOL"}
        if pos.get("asset_type") == asset_type:
            logger.warning(f"RISK_GATE: Asset type '{asset_type}' already occupied by {pos.get('symbol')}.")
            return {"allowed": False, "reason": "DUPLICATE_ASSET_TYPE"}

    # [4] 전략 기반 사이징 산출
    if unit_size <= 0:
        return {"allowed": False, "reason": "INVALID_SIZE_CONFIG"}

    return {
        "allowed": True,
        "size": unit_size,
        "reason": "PASS_ALL_RISK_FILTERS"
    }