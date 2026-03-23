import os
import sys
import logging
import yaml
from typing import Dict, Any, List

# =============================================================================
# IRONCLAD_V30.1_FINAL: CORE ORCHESTRATOR (run.py)
# FIX: AUDIT SEQUENCE, NO_ENTRY MODE, TYPE-SAFE HANDLER, INTEGRITY LOOP
# =============================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("IRONCLAD_RUNTIME")

# [보안 모듈 경로 교정] - GUARDS 디렉터리 경로 명확화
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
            "RUNTIME": self.base_path
        }
        # [RISK 해결] 기본값 자동 생성 없이 설정 로드 (실패 시 즉시 RuntimeError)
        self.system_config = self._load_config()
        setup_guard_path(self.root_path)

    def _load_config(self) -> Dict[str, Any]:
        config_path = os.path.join(self.paths["LOCKED"], "system_config.yaml")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if not config: raise ValueError("Empty config")
                return config
        except Exception as e: 
            raise RuntimeError(f"CONFIG_LOAD_FAILURE: {str(e)}")

    def run(self):
        """감사 기준 절대 순서(Scheduler -> Loader -> Selector -> Regime -> Entry) 준수"""
        # [모듈 일괄 임포트]
        from exception_handler import handle_critical_failure
        from preflight_gate import run_preflight_checks
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

        inc_dir = os.path.join(self.paths["EVIDENCE"], "incident")
        state_path = os.path.join(self.paths["STATE"], "state.json")

        try:
            # [PHASE 1] 초기 검증 및 보안 가동
            run_preflight_checks(self.paths)
            self.guard = IntegrityGuard(self.paths["LOCKED"])
            self.guard.check() # 1차 무결성 점검
            
            self.current_state = load_state(state_path)

            # [PHASE 2] 감사 순서 1: SCHEDULER (TRADE/NO_ENTRY/FORCE_EXIT/CLOSED)
            mode = get_current_mode()
            if mode == "CLOSED": 
                logger.info("SYSTEM_HALT: Market is closed.")
                return

            # [PHASE 3] 전략 파이프라인 (순서: Loader -> Selector -> Regime)
            # 2. data_loader (Top-N 제한 적용)
            market_data = load_market_data(["STOCK", "CRYPTO"], self.paths["STRATEGY"])
            
            # 3. selector (후보 압축)
            candidates = select_candidates(market_data, self.paths["STRATEGY"])
            
            self.guard.check() # 주요 분기점 무결성 체크

            # 4. regime_filter (장세 판단)
            if evaluate_market_regime(candidates, self.paths["STRATEGY"]):
                
                # 5. entry_engine (신호 생성 - TRADE 모드에서만 신규 진입)
                if mode == "TRADE":
                    raw_signals = generate_signals(candidates, self.paths["STRATEGY"])
                    
                    # 6. risk_gate (리스크 검증 및 비중 산출)
                    approved_signals = []
                    for sig in raw_signals:
                        res = validate_risk_and_size(sig, self.current_state, self.paths["STRATEGY"])
                        # allowed=True 확인 필수
                        if res.get("allowed"):
                            sig.update({"volume": res.get("size"), "risk_reason": res.get("reason")})
                            approved_signals.append(sig)

                    # 7. pre_order_check (최종 데이터 검증)
                    final_signals = validate_before_order(approved_signals, mode, self.current_state.get("positions", []), self.system_config)

                    # 8. order_manager (주문 실행)
                    if final_signals:
                        self.guard.check() # 주문 직전 무결성 최종 확인
                        execution_results = execute_orders(final_signals)
                        
                        # [PHASE 4] 사후 처리 (Fill -> State -> Ledger)
                        fills = track_fills(execution_results)
                        save_state(self.current_state, state_path)
                        record_to_ledger(fills, inc_dir)
            
            # [PHASE 5] 사후 처리 및 대조
            from exit_engine import process_exits
            from position_reconciler import reconcile_positions

            # 12. exit_engine 호출 (순서 준수)
            exit_results = process_exits(mode, self.current_state, self.paths["STRATEGY"])

            # 13. position_reconciler 호출 (SSOT 경로 전달)
            # [FIX] self.paths["STATE"] 내부의 state.json 경로를 명시적으로 주입
            state_file_path = os.path.join(self.paths["STATE"], "state.json")
            self.current_state = reconcile_positions(
                current_state=self.current_state, 
                exit_results=exit_results, 
                state_path=state_file_path
            )           
            
            self.guard.check() # 사이클 종료 전 무결성 확인
            logger.info(f"CYCLE_COMPLETE: Mode={mode} | Success.")

        except Exception as e:
            # [FIX] 타입 일치: paths(dict) 대신 inc_dir(str) 전달
            handle_critical_failure(reason=str(e), incident_dir=inc_dir)

if __name__ == "__main__":
    engine = IroncladEngine()
    engine.run()