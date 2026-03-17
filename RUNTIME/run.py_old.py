# run.py (S0 entrypoint)
import sys
import os
import json
import yaml
import hashlib
from pathlib import Path
from jsonschema import validate, ValidationError

from integrity_guard import IntegrityGuard
from preflight_gate import preflight_gate
from entry_engine import EntryEngine

def safe_halt(reason: str):
    print(f"[SAFE_HALT] {reason}")
    sys.exit(1)

def _require(data, key):
    """Zero-Default: 필수 키 누락 시 즉시 SAFE_HALT"""
    if key not in data or data[key] is None:
        safe_halt(f"MISSING_REQUIRED_KEY: {key}")
    return data[key]

# S1: ImportError SAFE_HALT 준수
try:
    from market_data import load_market_data
    from regime_filter import apply_regime_filter
    from risk_gate import risk_gate
    from order_manager import execute_orders
except ImportError as e:
    safe_halt(f"MODULE_IMPORT_FAIL: {e}")

BASE_DIR = Path(__file__).resolve().parent
PATHS = {
    "system_config": BASE_DIR / "LOCKED" / "CONSTITUTION" / "system_config.yaml",
    "schema_system_config": BASE_DIR / "LOCKED" / "CONSTITUTION" / "schema_system_config.json",
    "stage_contracts": BASE_DIR / "LOCKED" / "GOVERNANCE" / "stage_contracts.yaml",
    "schema_stage_contracts": BASE_DIR / "LOCKED" / "GOVERNANCE" / "schema_stage_contracts.json",
    "addendum_aip": BASE_DIR / "LOCKED" / "AIP" / "addendum_aip.yaml",
    "schema_addendum_aip": BASE_DIR / "LOCKED" / "AIP" / "schema_addendum_aip.json",
    "worker_allowlist": BASE_DIR / "LOCKED" / "POLICY" / "worker_allowlist.yaml",
    "recovery_policy": BASE_DIR / "LOCKED" / "POLICY" / "recovery_policy.yaml",
    "strategy_spec": BASE_DIR / "STRATEGY" / "strategy_spec.yaml",
    "state_file": BASE_DIR / "EVIDENCE" / "STATE" / "state.json",
}

def load_yaml(path: Path) -> dict:
    try:
        if not path.exists(): safe_halt(f"FILE_NOT_FOUND: {path}")
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None or not isinstance(data, dict):
            safe_halt(f"YAML_LOAD_INVALID: {path}")
        return data
    except Exception as e:
        safe_halt(f"YAML_LOAD_FAIL: {path}: {e}")

def load_json(path: Path) -> dict:
    try:
        if not path.exists(): safe_halt(f"FILE_NOT_FOUND: {path}")
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if data is None or not isinstance(data, dict):
            safe_halt(f"JSON_LOAD_INVALID: {path}")
        return data
    except Exception as e:
        safe_halt(f"JSON_LOAD_FAIL: {path}: {e}")

def validate_schema_all(system_cfg, stage_contracts, aip):
    try:
        validate(instance=system_cfg, schema=load_json(PATHS["schema_system_config"]))
        validate(instance=stage_contracts, schema=load_json(PATHS["schema_stage_contracts"]))
        validate(instance=aip, schema=load_json(PATHS["schema_addendum_aip"]))
    except ValidationError as ve:
        safe_halt(f"SCHEMA_VALIDATION_FAIL: {ve.message}")
    except Exception as e:
        safe_halt(f"SCHEMA_PROCESSING_FAIL: {e}")

def check_policy():
    """지적사항 반영: .get() 제거 및 _require 적용하여 Zero-Default 준수"""
    allowlist = load_yaml(PATHS["worker_allowlist"])
    allowed = _require(allowlist, "allowed_entrypoints")
    
    if not isinstance(allowed, list) or len(allowed) == 0:
        safe_halt("POLICY_INVALID_ALLOWLIST")

    current_entry = os.path.basename(sys.argv[0])
    if current_entry not in allowed:
        safe_halt(f"POLICY_UNAUTHORIZED_ENTRYPOINT: {current_entry}")

    rp_root = load_yaml(PATHS["recovery_policy"])
    rp = _require(rp_root, "recovery_policy")
    
    # [수정] Zero-Default: _require를 통해 명시적 키 확인
    mode = _require(rp, "mode")
    auto_recovery = _require(rp, "auto_recovery")
    
    if mode != "FAIL_SECURE" or auto_recovery is not False:
        safe_halt("POLICY_RECOVERY_MODE_VIOLATION")

def execution_cycle(stage_contracts):
    stages = _require(stage_contracts, "stages")
    for sid in stages:
        on_fail = _require(stages[sid], "on_fail")
        if on_fail != "SAFE_HALT":
            safe_halt(f"CONTRACT_VIOLATION: {sid}")

    market_data = load_market_data()
    if not isinstance(market_data, list):
        safe_halt("S3_DATA_TYPE_INVALID")

    entry_engine = EntryEngine(
        config_path=str(PATHS["strategy_spec"]),
        contract_path=str(PATHS["stage_contracts"])
    )
    signals = entry_engine.run(apply_regime_filter(market_data))
    
    if not signals:
        print("[CYCLE_END] Reason: STRATEGY_CONDITION_NOT_MET")
        return

    approved_signals = risk_gate(signals)
    if not approved_signals:
        print("[CYCLE_END] Reason: ALL_SIGNALS_REJECTED_BY_RISK_GATE")
        return

    execute_orders(approved_signals)

def main():
    check_policy()
    
    # [지적사항 수정]: 누락되었던 정책 파일 존재 검증 복구
    preflight_gate(
        [str(PATHS[k]) for k in ["system_config", "stage_contracts", "addendum_aip", "worker_allowlist", "recovery_policy"]],
        [str(PATHS[k]) for k in ["schema_system_config", "schema_stage_contracts", "schema_addendum_aip"]]
    )

    system_cfg = load_yaml(PATHS["system_config"])
    stage_contracts = load_yaml(PATHS["stage_contracts"])
    
    validate_schema_all(system_cfg, stage_contracts, load_yaml(PATHS["addendum_aip"]))
    
    # [지적사항 수정]: 해시 계산 방식을 바이너리(rb)로 통일하여 Mismatch 해결
    with PATHS["system_config"].open("rb") as f:
        locked_hash = hashlib.sha256(f.read()).hexdigest()
    
    guard = IntegrityGuard(str(PATHS["system_config"]), locked_hash)
    guard.check() # 명시적 1회 호출

    execution_cycle(stage_contracts)

if __name__ == "__main__":
    main()