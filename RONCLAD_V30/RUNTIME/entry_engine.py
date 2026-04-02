# ============================================================
# IRONCLAD_V31 - Strategic Entry Engine (V31.0 Structural Split)
# ============================================================
import os
import yaml
import operator
from typing import List, Dict, Any
import pandas as pd

# [2-1] OPERATORS 정의 전체 (하위 호환 유지)
OPERATORS = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "==": operator.eq
}

# [2-2] load_strategy_entry_rules 함수 전체 (수정 없음)
def load_strategy_entry_rules(strategy_path: str) -> Dict[str, Any]:
    """모든 전략 폴더에서 entry_rules.yaml을 수집하여 반환함"""
    all_rules = {}
    if not os.path.exists(strategy_path):
        raise RuntimeError(f"STRATEGY_ROOT_MISSING: {strategy_path}")

    for folder in os.listdir(strategy_path):
        folder_path = os.path.join(strategy_path, folder)
        if not os.path.isdir(folder_path):
            continue
        
        rules_file = os.path.join(folder_path, "entry_rules.yaml")
        if os.path.exists(rules_file):
            try:
                with open(rules_file, "r", encoding="utf-8") as f:
                    rules_data = yaml.safe_load(f)
                    if rules_data and "entry" in rules_data:
                        all_rules[folder] = rules_data["entry"]
            except Exception as e:
                print(f"[ERROR] Failed to load {rules_file}: {e}")
    
    return all_rules

# [2-3] evaluate_condition 함수 전체 (판단 전용: history.iloc[-1] 기반)
def evaluate_condition(last_row: pd.Series, condition: Dict[str, Any]) -> bool:
    """YAML 정의 기반 단일 조건 평가 (시계열 마지막 행 기준)"""
    field = condition.get("field")
    op_str = condition.get("op")
    
    if field not in last_row:
        raise RuntimeError(f"CONDITION_FIELD_MISSING: {field}")
    if op_str not in OPERATORS:
        raise RuntimeError(f"UNSUPPORTED_OPERATOR: {op_str}")

    left_val = last_row[field]
    op_func = OPERATORS[op_str]

    if "value" in condition:
        right_val = float(condition["value"])
    elif "ref" in condition:
        ref_field = condition["ref"]
        if ref_field not in last_row:
            raise RuntimeError(f"CONDITION_REF_FIELD_MISSING: {ref_field}")
        
        multiplier = float(condition.get("multiplier", 1.0))
        right_val = last_row[ref_field] * multiplier
    else:
        raise RuntimeError(f"CONDITION_TARGET_MISSING: {field}")

    return op_func(left_val, right_val)

# [2-4] generate_signals (V31.0: history 판단 + current 실행 분리)
def generate_signals(
    data_bundle: Dict[str, Dict[str, Any]], 
    strategy_path: str, 
    state: Dict[str, Any], 
    system_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    [V31.0 시그널 생성 엔진]
    1. history: 전략 조건 및 데이터 계약(asset_type) 판단
    2. current: 실제 시그널 생성 시 실행값(price, asset_type) 추출
    """
    signals = []
    
    strategy_rules = load_strategy_entry_rules(strategy_path)
    if not strategy_rules:
        return []

    # [V31.0] 입력 구조 수정: bundle 단위 순회
    for symbol, bundle in data_bundle.items():
        current = bundle["current"]
        history = bundle["history"]

        if history.empty:
            continue
            
        # [판단 구조] 모든 조건 판단은 history 기반
        if "asset_type" not in history.columns:
            raise RuntimeError(f"DATA_CONTRACT_VIOLATION: asset_type missing for {symbol}")

        last_row = history.iloc[-1]

        # 각 전략별 진입 조건 검사
        for strategy_name, entry_cfg in strategy_rules.items():
            conditions = entry_cfg.get("conditions", [])
            if not conditions:
                continue

            is_qualified = True
            for cond in conditions:
                try:
                    if not evaluate_condition(last_row, cond):
                        is_qualified = False
                        break
                except Exception:
                    is_qualified = False
                    break
            
            # [실행 구조] 모든 조건을 통과한 경우 current(snapshot)를 사용하여 시그널 생성
            if is_qualified:
                signals.append({
                    "symbol": symbol,
                    "side": "BUY",
                    "price": float(current["price"]),
                    "asset_type": current["asset_type"],
                    "strategy_name": strategy_name,
                    "risk_per_trade": entry_cfg.get("risk_per_trade"),
                    "stop_distance": entry_cfg.get("stop_distance")
                })
                # 1자산 1신호 원칙
                break

    return signals