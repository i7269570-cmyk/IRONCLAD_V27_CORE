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


def load_yaml(path: str) -> dict:
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        if data is None:
            safe_halt(f"Config Load Failure: empty -> {path}")

        if not isinstance(data, dict):
            safe_halt(f"Config Load Failure: invalid type -> {path}")

        return data

    except Exception as e:
        safe_halt(f"Config Load Failure: {path}: {str(e)}")


def load_json(path: str) -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)

    except Exception as e:
        safe_halt(f"Schema Load Failure: {path}: {str(e)}")


def load_configs() -> dict:

    system_cfg = load_yaml(CONFIG_FILES[0])
    stage_contracts = load_yaml(CONFIG_FILES[1])
    addendum_aip = load_yaml(CONFIG_FILES[2])

    return {
        "system": system_cfg,
        "contracts": stage_contracts,
        "aip": addendum_aip
    }


def validate_schema(configs: dict):

    try:

        schema_system = load_json(SCHEMA_FILES[0])
        validate(instance=configs["system"], schema=schema_system)

        schema_contracts = load_json(SCHEMA_FILES[1])
        validate(instance=configs["contracts"], schema=schema_contracts)

        schema_aip = load_json(SCHEMA_FILES[2])
        validate(instance=configs["aip"], schema=schema_aip)

    except ValidationError as ve:
        safe_halt(f"Schema Validation Failure: {ve.message}")

    except Exception as e:
        safe_halt(f"Schema Processing Failure: {str(e)}")


def integrity_guard_init(system_cfg: dict) -> str:

    try:
        config_str = json.dumps(system_cfg, sort_keys=True)

        return hashlib.sha256(
            config_str.encode()
        ).hexdigest()

    except Exception as e:
        safe_halt(f"Integrity Guard Init Failure: {str(e)}")


def execution_cycle(configs: dict):

    try:

        contracts = configs["contracts"]

        if not isinstance(contracts, dict):
            safe_halt("Stage Contracts Invalid")

        for stage, contract in contracts.items():

            if not isinstance(contract, dict):
                safe_halt(f"Contract Invalid: {stage}")

            if contract.get("on_fail") != "SAFE_HALT":
                safe_halt(
                    f"Contract Violation: {stage} on_fail must be SAFE_HALT"
                )

    except Exception as e:
        safe_halt(f"Execution Cycle Failure: {str(e)}")


def main():

    preflight_gate(CONFIG_FILES, SCHEMA_FILES)

    configs = load_configs()

    validate_schema(configs)

    locked_hash = integrity_guard_init(configs["system"])

    guard = IntegrityGuard(
        CONFIG_FILES[0],
        locked_hash
    )

    guard.check()

    execution_cycle(configs)


if __name__ == "__main__":
    main()