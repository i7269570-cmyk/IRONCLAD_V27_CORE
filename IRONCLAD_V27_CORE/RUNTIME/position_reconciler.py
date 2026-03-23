# position_reconciler.py
import sys
import json
from pathlib import Path

def safe_halt(reason: str):
    print(f"[SAFE_HALT][POSITION_RECONCILER] {reason}")
    sys.exit(1)

def reconcile_positions(exchange, state_path, system_config):
    # 1. 사전 검증: try 외부에서 수행하여 safe_halt 포획 방지
    if not state_path.exists():
        safe_halt(f"STATE_FILE_NOT_FOUND: {state_path}")
    
    limits = system_config.get("safety_limits") # main에서 검증된 SSOT
    if not limits or "position_tolerance" not in limits:
        safe_halt("SSOT_MISSING: safety_limits.position_tolerance")
    
    tolerance = limits["position_tolerance"]

    # 2. 데이터 로드 및 대조
    try:
        exchange_balances = exchange.get_balances()
        with state_path.open('r', encoding='utf-8') as f:
            internal_state = json.load(f)
        
        if "positions" not in internal_state:
            safe_halt("STATE_KEY_MISSING: positions")
        internal_positions = internal_state["positions"]

        # 3. 양방향 대조 (Bidirectional Strict Check)
        for asset, exch_val in exchange_balances.items():
            if asset not in internal_positions:
                safe_halt(f"RECON_INTERNAL_ASSET_MISSING: {asset}")
            
            diff = abs(float(exch_val) - float(internal_positions[asset]))
            if diff > tolerance:
                safe_halt(f"RECON_MISMATCH: {asset} (Diff: {diff} > Tol: {tolerance})")

        for asset in internal_positions.keys():
            if asset not in exchange_balances:
                safe_halt(f"RECON_EXCHANGE_ASSET_MISSING: {asset}")

        # 4. 상태 동기화
        internal_state["positions"] = exchange_balances
        with state_path.open('w', encoding='utf-8') as f:
            json.dump(internal_state, f, indent=4)

    except json.JSONDecodeError:
        safe_halt("STATE_FILE_CORRUPTED")
    except Exception as e:
        safe_halt(f"RECON_UNEXPECTED_FAILURE: {e}")

    return True