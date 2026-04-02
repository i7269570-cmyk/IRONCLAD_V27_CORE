# ============================================================
# IRONCLAD_V31.16 - Final Pipeline Integration (Full State Reconciliation)
# ============================================================
import os
from typing import Dict, Any, List

# [Standard] Module Imports
from scheduler import get_current_mode
from data_loader import load_market_data
from indicator_calc import calculate_indicators
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
from state_manager import save_state
from exception_handler import handle_critical_error

def run_pipeline(paths: dict, strategy_path: str, state_path: str, evidence_path: str, state: Dict[str, Any], system_config: Dict[str, Any]):
    """
    [V31.16 Pipeline Specification]
    Goal: Connect fill_results to reconciler for full state update.
    Ensure all state mutations are handled exclusively by reconcile_positions.
    """
    try:
        # 1. scheduler
        mode = get_current_mode()
        if mode == "CLOSED":
            save_state(state, state_path)
            return state

        # 2. data_loader (V31 Structure)
        asset_types = ["STOCK", "CRYPTO"]
        data_bundle = load_market_data(asset_types, strategy_path)
        
        for symbol in data_bundle:
            data_bundle[symbol]["history"] = calculate_indicators(data_bundle[symbol]["history"])

        # Selector_input Generation & Field Integrity Validation
        selector_input = []
        for symbol, bundle in data_bundle.items():
            current = bundle["current"]
            
            required_fields = ["price", "asset_type", "change_rate", "value"]
            for field in required_fields:
                if field not in current or current[field] is None:
                    raise RuntimeError(f"MISSING_FIELD: {field} for {symbol}")

            selector_input.append({
                "symbol": symbol,
                "price": current["price"],
                "asset_type": current["asset_type"],
                "change_rate": current["change_rate"],
                "value": current["value"]
            })

        # 3. selector & 4. regime_filter processing
        fill_results = []
        if mode == "TRADE":
            selected = select_candidates(selector_input, strategy_path)
            regime_ok = evaluate_market_regime(selector_input, strategy_path)
            
            if not regime_ok:
                save_state(state, state_path)
                return state

            # 5. entry_engine
            entry_signals = generate_signals(data_bundle, strategy_path, state, system_config)

            # 6. risk_gate
            candidate_signals = []
            for sig in entry_signals:
                risk_res = validate_risk_and_size(sig, state, system_config)
                if risk_res.get("allowed"):
                    sig["volume"] = risk_res["size"]
                    candidate_signals.append(sig)

            # [Spec] validate_before_order
            approved_signals = []
            if candidate_signals:
                approved_signals = validate_before_order(
                    candidate_signals, 
                    mode, 
                    state["positions"], 
                    system_config
                )

            # [Spec] execute_orders -> track_fills (Fills are NOT applied to state here)
            if approved_signals:
                order_results = execute_orders(approved_signals)
                fills_input = order_results.get("results", [])
                fill_results = track_fills(fills_input, state)

        # 11. exit_engine
        exit_results = {}
        if mode in ["TRADE", "NO_ENTRY", "FORCE_EXIT"]:
            exit_list = process_exits(data_bundle, state, strategy_path)
            
            for item in exit_list:
                symbol = item["symbol"]
                if symbol in exit_results:
                    raise RuntimeError(f"DUPLICATE_EXIT_SIGNAL: {symbol}")
                exit_results[symbol] = item

        # [Spec] ledger_writer recording
        if fill_results or exit_results:
            record_to_ledger(
                {
                    "fills": fill_results,
                    "exits": exit_results
                },
                evidence_path
            )

        # 12. position_reconciler (The ONLY point where state is updated)
        # [V31.16] Corrected call signature to include both entries and exits.
        if fill_results or exit_results:
            state = reconcile_positions(
                state, 
                {
                    "entries": fill_results,
                    "exits": exit_results
                }, 
                state_path
            )

        # 13. state_manager final save
        save_state(state, state_path)
        return state

    except Exception as e:
        handle_critical_error(
            str(e),
            paths
        )
        raise