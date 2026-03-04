import sys
import yaml
import json
import hashlib
from jsonschema import validate, ValidationError
from integrity_guard import IntegrityGuard
from preflight_gate import preflight_gate

CONFIG_FILES = [
    "system_config.yaml",
    "stage_contracts.yaml",
    "addendum_aip.yaml"
]

SCHEMA_FILES = [
    "schema_system_config.json",
    "schema_stage_contracts.json",
    "schema_addendum_aip.json"
]

def safe_halt(reason: str):
    print(f"[SAFE_HALT] {reason}")
    sys.exit(1)

def load_configs() -> dict:
    try:
        with open(CONFIG_FILES[0], "r") as f:
            system_cfg = yaml.safe_load(f)
        with open(CONFIG_FILES[1], "r") as f:
            stage_contracts = yaml.safe_load(f)
        with open(CONFIG_FILES[2], "r") as f:
            addendum_aip = yaml.safe_load(f)
        
        return {
            "system": system_cfg,
            "contracts": stage_contracts,
            "aip": addendum_aip
        }
    except Exception as e:
        safe_halt(f"Config Load Failure: {str(e)}")

def validate_schema(configs: dict):
    schema_map = {
        "system": SCHEMA_FILES[0],
        "contracts": SCHEMA_FILES[1],
        "aip": SCHEMA_FILES[2]
    }
    try:
        for key, schema_path in schema_map.items():
            with open(schema_path, "r") as sf:
                schema = json.load(sf)
            validate(instance=configs[key], schema=schema)
    except ValidationError as ve:
        safe_halt(f"Schema Validation Failure: {ve.message}")
    except Exception as e:
        safe_halt(f"Schema Processing Failure: {str(e)}")

def integrity_guard_init(configs: dict) -> str:
    try:
        config_str = json.dumps(configs["system"], sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    except Exception as e:
        safe_halt(f"Integrity Guard Init Failure: {str(e)}")

def execution_cycle():
    return

def main():
    try:
        # 1. Preflight File Existence Check
        preflight_gate(CONFIG_FILES, SCHEMA_FILES)

        # 2. Load
        configs = load_configs()
        
        # 3. Schema Validation
        validate_schema(configs)
        
        # 4. Integrity Guard (SSOT Hash Lock)
        locked_hash = integrity_guard_init(configs)
        guard = IntegrityGuard(CONFIG_FILES[0], locked_hash)
        
        # 5. Main Loop Entry
        while True:
            # 5-1. SSOT Integrity Check
            guard.check()
            
            # 5-2. Execution Cycle
            execution_cycle()
            
    except Exception as e:
        safe_halt(f"Main Loop Exception: {str(e)}")

if __name__ == "__main__":
    main()