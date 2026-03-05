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


def safe_halt(reason: str):
    print(f"[SAFE_HALT] {reason}")
    sys.exit(1)


BASE_DIR = Path(__file__).resolve().parent

PATHS = {
    # LOCKED
    "system_config": BASE_DIR / "LOCKED" / "CONSTITUTION" / "system_config.yaml",
    "schema_system_config": BASE_DIR / "LOCKED" / "CONSTITUTION" / "schema_system_config.json",
    "stage_contracts": BASE_DIR / "LOCKED" / "GOVERNANCE" / "stage_contracts.yaml",
    "schema_stage_contracts": BASE_DIR / "LOCKED" / "GOVERNANCE" / "schema_stage_contracts.json",
    "addendum_aip": BASE_DIR / "LOCKED" / "AIP" / "addendum_aip.yaml",
    "schema_addendum_aip": BASE_DIR / "LOCKED" / "AIP" / "schema_addendum_aip.json",
    # POLICY
    "worker_allowlist": BASE_DIR / "LOCKED" / "POLICY" / "worker_allowlist.yaml",
    "recovery_policy": BASE_DIR / "LOCKED" / "POLICY" / "recovery_policy.yaml",
}


def load_yaml(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None or not isinstance(data, dict):
            safe_halt(f"YAML_LOAD_INVALID: {path}")
        return data
    except SystemExit:
        raise
    except Exception as e:
        safe_halt(f"YAML_LOAD_FAIL: {path}: {e}")


def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if data is None or not isinstance(data, dict):
            safe_halt(f"JSON_LOAD_INVALID: {path}")
        return data
    except SystemExit:
        raise
    except Exception as e:
        safe_halt(f"JSON_LOAD_FAIL: {path}: {e}")


def check_policy():
    # 1) allowlist
    allowlist = load_yaml(PATHS["worker_allowlist"])
    allowed = allowlist.get("allowed_entrypoints")
    if not isinstance(allowed, list) or len(allowed) < 1:
        safe_halt("POLICY_INVALID_ALLOWLIST")

    current_entry = os.path.basename(sys.argv[0])
    if current_entry not in allowed:
        safe_halt(f"POLICY_UNAUTHORIZED_ENTRYPOINT: {current_entry}")

    # 2) recovery policy (fail-secure)
    rp = load_yaml(PATHS["recovery_policy"])
    r = rp.get("recovery_policy")
    if not isinstance(r, dict):
        safe_halt("POLICY_INVALID_RECOVERY")

    if r.get("mode") != "FAIL_SECURE":
        safe_halt("POLICY_RECOVERY_MODE_NOT_FAIL_SECURE")

    if r.get("auto_recovery") is not False:
        safe_halt("POLICY_AUTO_RECOVERY_NOT_FALSE")


def validate_schema_all(system_cfg: dict, stage_contracts: dict, aip: dict):
    try:
        validate(instance=system_cfg, schema=load_json(PATHS["schema_system_config"]))
        validate(instance=stage_contracts, schema=load_json(PATHS["schema_stage_contracts"]))
        validate(instance=aip, schema=load_json(PATHS["schema_addendum_aip"]))
    except ValidationError as ve:
        safe_halt(f"SCHEMA_VALIDATION_FAIL: {ve.message}")
    except SystemExit:
        raise
    except Exception as e:
        safe_halt(f"SCHEMA_PROCESSING_FAIL: {e}")


def integrity_guard_init(system_cfg: dict) -> str:
    try:
        cfg_str = json.dumps(system_cfg, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(cfg_str.encode("utf-8")).hexdigest()
    except SystemExit:
        raise
    except Exception as e:
        safe_halt(f"INTEGRITY_INIT_FAIL: {e}")


def get_stage_map(stage_contracts: dict) -> dict:
    stages = stage_contracts.get("stages")
    if not isinstance(stages, dict) or len(stages) < 1:
        safe_halt("STAGE_CONTRACTS_INVALID_STAGES")
    return stages


def execution_cycle(stage_contracts: dict):
    stages = get_stage_map(stage_contracts)

    # deterministic order from contract keys (no hardcoded stage list)
    def _k(stage_id: str) -> int:
        if not isinstance(stage_id, str) or not stage_id.startswith("S"):
            safe_halt(f"STAGE_ID_INVALID: {stage_id}")
        num = stage_id[1:]
        if not num.isdigit():
            safe_halt(f"STAGE_ID_INVALID: {stage_id}")
        return int(num)

    ordered = sorted(stages.keys(), key=_k)

    for sid in ordered:
        contract = stages.get(sid)
        if not isinstance(contract, dict):
            safe_halt(f"CONTRACT_INVALID: {sid}")

        # TRINITY failover: SAFE_HALT only
        if contract.get("on_fail") != "SAFE_HALT":
            safe_halt(f"CONTRACT_VIOLATION_ON_FAIL: {sid}")

    # NOTE: S1~S11 business logic intentionally not implemented yet.
    return


def main():
    # POLICY first
    check_policy()

    # Preflight existence check (LOCKED refs only)
    config_files = [
        str(PATHS["system_config"]),
        str(PATHS["stage_contracts"]),
        str(PATHS["addendum_aip"]),
        str(PATHS["worker_allowlist"]),
        str(PATHS["recovery_policy"]),
    ]
    schema_files = [
        str(PATHS["schema_system_config"]),
        str(PATHS["schema_stage_contracts"]),
        str(PATHS["schema_addendum_aip"]),
    ]
    preflight_gate(config_files, schema_files)

    # Load
    system_cfg = load_yaml(PATHS["system_config"])
    stage_contracts = load_yaml(PATHS["stage_contracts"])
    aip = load_yaml(PATHS["addendum_aip"])

    # Schema validation
    validate_schema_all(system_cfg, stage_contracts, aip)

    # Integrity lock + runtime check
    locked_hash = integrity_guard_init(system_cfg)
    guard = IntegrityGuard(str(PATHS["system_config"]), locked_hash)
    guard.check()

    # One cycle (n8n triggers repeat)
    execution_cycle(stage_contracts)


if __name__ == "__main__":
    main()