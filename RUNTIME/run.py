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
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None or not isinstance(data, dict):
            safe_halt(f"YAML_LOAD_INVALID: {path}")
        return data
    except Exception as e:
        safe_halt(f"YAML_LOAD_FAIL: {path}: {e}")

def load_json(path: Path) -> dict:
    try:
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
    """Zero-Default: check_policy() 준수"""
    allowlist = load_yaml(PATHS["worker_allowlist"])
    
    if "allowed_entrypoints" not in allowlist:
        safe_halt("POLICY_KEY_MISSING: allowed_entrypoints")
    
    allowed = allowlist["allowed_entrypoints"]
    if not isinstance(allowed, list) or len(allowed) == 0:
        safe_halt("POLICY_INVALID_ALLOWLIST")

    current_entry = os.path.basename(sys.argv[0])
    if current_entry not in allowed:
        safe_halt(f"POLICY_UNAUTHORIZED_ENTRYPOINT: {current_entry}")

    rp_root = load_yaml(PATHS["recovery_policy"])
    if "recovery_policy" not in rp_root:
        safe_halt("POLICY_KEY_MISSING: recovery_policy")
    
    rp = rp_root["recovery_policy"]
    if "mode" not in rp or "auto_recovery" not in rp:
        safe_halt("POLICY_RECOVERY_KEYS_MISSING")
    
    if rp["mode"] != "FAIL_SECURE" or rp["auto_recovery"] is not False:
        safe_halt("POLICY_RECOVERY_MODE_VIOLATION")

def execution_cycle(stage_contracts):
    """Zero-Default & Type Validation 강화"""
    
    if "stages" not in stage_contracts:
        safe_halt("CONTRACT_KEY_MISSING: stages")
    
    stages = stage_contracts["stages"]
    
    # S3~S7 파이프라인 계약 준수 확인
    for sid in ["S3", "S4", "S5", "S6", "S7"]:
        if sid not in stages:
            safe_halt(f"CONTRACT_STAGE_MISSING: {sid}")
        # Zero-Default: .get() 제거, on_fail 키 존재 강제 확인
        if "on_fail" not in stages[sid]:
            safe_halt(f"CONTRACT_ON_FAIL_MISSING: {sid}")
        if stages[sid]["on_fail"] != "SAFE_HALT":
            safe_halt(f"CONTRACT_VIOLATION: {sid} on_fail must be SAFE_HALT")

    # S3: Market Data Type Validation
    market_data = load_market_data()
    if not isinstance(market_data, list):
        safe_halt("S3_DATA_TYPE_INVALID: market_data must be a list")

    # S4 -> S7 파이프라인 실행
    filtered_data = apply_regime_filter(market_data)
    
    entry_engine = EntryEngine(
        config_path="STRATEGY/strategy_spec.yaml",
        contract_path="LOCKED/GOVERNANCE/stage_contracts.yaml"
    )
    signals = entry_engine.run(filtered_data)
    
    if not signals:
        return

    approved_signals = risk_gate(signals)
    if approved_signals:
        execute_orders(approved_signals)

def main():
    check_policy()
    
    config_paths = [str(PATHS[k]) for k in ["system_config", "stage_contracts", "addendum_aip", "worker_allowlist", "recovery_policy"]]
    schema_paths = [str(PATHS[k]) for k in ["schema_system_config", "schema_stage_contracts", "schema_addendum_aip"]]
    preflight_gate(config_paths, schema_paths)

    system_cfg = load_yaml(PATHS["system_config"])
    stage_contracts = load_yaml(PATHS["stage_contracts"])
    aip = load_yaml(PATHS["addendum_aip"])

    validate_schema_all(system_cfg, stage_contracts, aip)
    
    cfg_str = json.dumps(system_cfg, sort_keys=True, separators=(",", ":"))
    locked_hash = hashlib.sha256(cfg_str.encode("utf-8")).hexdigest()
    IntegrityGuard(str(PATHS["system_config"]), locked_hash).check()

    execution_cycle(stage_contracts)

if __name__ == "__main__":
    main()