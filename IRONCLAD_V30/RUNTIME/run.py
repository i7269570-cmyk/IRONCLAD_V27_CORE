import os
import sys
import logging
import yaml
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE_DIR)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("IRONCLAD_RUNTIME")


def setup_guard_path(root_path):
    guard_path = os.path.join(root_path, "LOCKED", "GUARDS")
    if guard_path not in sys.path:
        sys.path.append(guard_path)


class IroncladEngine:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.root_path = os.path.dirname(self.base_path)
        self.paths = {
            "LOCKED": os.path.join(self.root_path, "LOCKED"),
            "STRATEGY": os.path.join(self.root_path, "STRATEGY"),
            "STATE": os.path.join(self.root_path, "STATE"),
            "EVIDENCE": os.path.join(self.root_path, "EVIDENCE"),
            "SYSTEM_CONFIG": os.path.join(self.root_path, "LOCKED", "system_config.yaml"),
            "RECOVERY_POLICY": os.path.join(self.root_path, "LOCKED", "recovery_policy.yaml"),
        }
        self.system_config = self._load_config()
        setup_guard_path(self.root_path)
        self.current_state: Dict[str, Any] = {}

    # =========================
    # 🔵 공통 유틸 (수정 금지)
    # =========================
    def _normalize_list_of_dict(self, data, name="data"):
        if isinstance(data, dict):
            data = [data]

        if not isinstance(data, list):
            raise TypeError(f"{name} must be list[dict], got {type(data)}")

        normalized = []
        for item in data:
            if isinstance(item, dict):
                normalized.append(item)
            elif isinstance(item, list):
                for sub in item:
                    if isinstance(sub, dict):
                        normalized.append(sub)

        for x in normalized:
            if not isinstance(x, dict):
                raise TypeError(f"{name} contains invalid type: {type(x)}")

        return normalized

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.paths["SYSTEM_CONFIG"], "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config if config else {}
        except Exception as e:
            raise RuntimeError(f"CONFIG_LOAD_FATAL: {str(e)}")

    def _validate_state(self) -> None:
        if not isinstance(self.current_state, dict):
            raise RuntimeError("STATE_INVALID: state is not dict")

        self.current_state.setdefault("positions", {})
        self.current_state.setdefault("capital", {})

        if not isinstance(self.current_state["positions"], dict):
            raise RuntimeError("STATE_INVALID: positions must be dict")

        if not isinstance(self.current_state["capital"], dict):
            raise RuntimeError("STATE_INVALID: capital must be dict")

        self.current_state["capital"].setdefault("total", 0)
        self.current_state["capital"].setdefault("stock_alloc", 0)
        self.current_state["capital"].setdefault("crypto_alloc", 0)

    def run(self):
        from state_manager import load_state, save_state
        from scheduler import get_current_mode
        from data_loader import load_market_data
        from selector import select_candidates
        from regime_filter import evaluate_market_regime
        from entry_engine import generate_signals
        from risk_gate import validate_risk_and_size
        from pre_order_check import validate_before_order
        from order_manager import execute_orders
        from fill_tracker import track_fills
        from ledger_writer import record_to_ledger
        from exit_engine import process_exits
        from position_reconciler import reconcile_positions
        from integrity_guard import IntegrityGuard
        from exception_handler import handle_critical_error

        state_file_path = os.path.join(self.paths["STATE"], "state.json")
        evidence_root = os.path.join(self.paths["EVIDENCE"], "incident")
        os.makedirs(evidence_root, exist_ok=True)

        try:
            self.guard = IntegrityGuard(self.paths["LOCKED"])
            self.guard.check()

            self.current_state = load_state(state_file_path)
            self._validate_state()

            mode = get_current_mode()
            if mode == "CLOSED":
                logger.info("SYSTEM_HALT: Market is closed.")
                return

            market_data = load_market_data(["STOCK", "CRYPTO"], self.paths["STRATEGY"])
            candidates = select_candidates(market_data, self.paths["STRATEGY"])

            if evaluate_market_regime(candidates, self.paths["STRATEGY"]):
                if mode == "TRADE":

                    raw_signals = generate_signals(
                        candidates,
                        self.paths["STRATEGY"],
                        self.current_state,
                    )

                    # =========================
                    # 🔥 raw_signals 완전 방어 (핵심)
                    # =========================
                    if isinstance(raw_signals, dict):
                        raw_signals = [raw_signals]

                    if not isinstance(raw_signals, list):
                        raw_signals = []

                    approved_signals = []

                    for sig in raw_signals:
                        if not isinstance(sig, dict):
                            continue

                        try:
                            res = validate_risk_and_size(sig, self.current_state, self.system_config)

                            if isinstance(res, dict) and res.get("allowed"):
                                sig["volume"] = res.get("size")
                                approved_signals.append(sig)

                        except Exception:
                            continue

                    # =========================
                    # 🔵 SIGNAL 정제
                    # =========================
                    final_signals = validate_before_order(
                        approved_signals,
                        mode,
                        self.current_state.get("positions", {}),
                        self.system_config,
                    )

                    final_signals = self._normalize_list_of_dict(final_signals, "signals")

                    # =========================
                    # 🔵 ORDER 실행
                    # =========================
                    if final_signals:
                        execution_results = execute_orders(final_signals)

                        execution_results = self._normalize_list_of_dict(
                            execution_results, "execution_results"
                        )

                        fills = track_fills(execution_results, self.current_state)
                        fills = self._normalize_list_of_dict(fills, "fills")

                        if len(fills) > 0:
                            logger.info(f"FILL_TRACKER_SUCCESS: {len(fills)} fills")
                            record_to_ledger(fills, evidence_root)
                            save_state(self.current_state, state_file_path)
                        else:
                            logger.warning("체결 내역 없음 (SKIP SAVE)")

            # =========================
            # 🔵 EXIT / RECONCILE
            # =========================
            exit_results = process_exits(mode, self.current_state, self.paths["STRATEGY"])
            safe_exit = exit_results if isinstance(exit_results, dict) else {}

            reconciled = reconcile_positions(self.current_state, safe_exit, state_file_path)

            if isinstance(reconciled, dict):
                self.current_state = reconciled

            self.current_state["positions"] = dict(self.current_state.get("positions", {}))

            # =========================
            # 🔵 FINAL SAVE
            # =========================
            self._validate_state()
            save_state(self.current_state, state_file_path)

            logger.info(
                f"CYCLE_COMPLETE: Mode={mode} | Active Positions={len(self.current_state.get('positions', {}))}"
            )

        except Exception as e:
            logger.error(f"RUNTIME_EXCEPTION: {str(e)}")
            handle_critical_error(str(e), self.paths)


if __name__ == "__main__":
    engine = IroncladEngine()
    engine.run()