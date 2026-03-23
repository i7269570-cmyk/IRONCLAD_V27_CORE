import os
import sys
import logging
import yaml
from typing import Dict, Any, List

# =============================================================================
# IRONCLAD_V30.1_FINAL: CORE ORCHESTRATOR (run.py)
# FIX: ARGUMENT SYNC, LOGIC CONSOLIDATION, PATH SSOT, ERROR HANDLING
# =============================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("IRONCLAD_RUNTIME")

def setup_guard_path(root_path):
    """보안 및 리스크 모듈이 위치한 LOCKED/GUARDS 경로를 시스템 패스에 추가한다."""
    guard_path = os.path.join(root_path, "LOCKED", "GUARDS")
    if guard_path not in sys.path:
        sys.path.append(guard_path)

class IroncladEngine:
    def __init__(self):
        # 1. 경로 설정 (SSOT)
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.root_path = os.path.dirname(self.base_path)
        self.paths = {
            "LOCKED": os.path.join(self.root_path, "LOCKED"),
            "STRATEGY": os.path.join(self.root_path, "STRATEGY"),
            "STATE": os.path.join(self.root_path, "STATE"),
            "EVIDENCE": os.path.join(self.root_path, "EVIDENCE"),
            "SYSTEM_CONFIG": os.path.join(self.root_path, "LOCKED", "system_config.yaml"),
            "RECOVERY_POLICY": os.path.join(self.root_path, "LOCKED", "recovery_policy.yaml")
        }
        
        # 2. 시스템 설정 로드 (기본값 없이 강제 로드)
        self.system_config = self._load_config()
        setup_guard_path(self.root_path)
        self.current_state = {}

    def _load_config(self) -> Dict[str, Any]:
        """system_config.yaml을 로드하며 실패 시 즉시 중단한다."""
        try:
            with open(self.paths["SYSTEM_CONFIG"], 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if not config: raise ValueError("EMPTY_CONFIG")
                return config
        except Exception as e: 
            raise RuntimeError(f"CONFIG_LOAD_FATAL: {str(e)}")

    def run(self):
        """감사 기준 6단계 공정 및 무결성 루프 실행"""
        # [모듈 지연 임포트: 경로 의존성 해결 후 로드]
        from exception_handler import handle_critical_error
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

        # 주요 경로 변수
        state_file_path = os.path.join(self.paths["STATE"], "state.json")
        evidence_root = self.paths["EVIDENCE"]

        try:
            # [PHASE 1] 무결성 및 상태 로드
            run_preflight_checks(self.paths)
            self.guard = IntegrityGuard(self.paths["LOCKED"])
            self.guard.check() 
            
            self.current_state = load_state(state_file_path)

            # [PHASE 2] SCHEDULER: 운영 모드 결정
            mode = get_current_mode()
            if mode == "CLOSED": 
                logger.info("SYSTEM_HALT: Market is closed.")
                return

            # [PHASE 3] 진입 파이프라인 (Loader -> Selector -> Regime)
            # 1. 데이터 로드
            market_data = load_market_data(["STOCK", "CRYPTO"], self.paths["STRATEGY"])
            
            # 2. 후보 종목 선정
            candidates = select_candidates(market_data, self.paths["STRATEGY"])
            
            self.guard.check() # 분기점 무결성 체크

            # 3. 장세 필터 및 진입 신호 생성
            if evaluate_market_regime(candidates, self.paths["STRATEGY"]):
                
                # TRADE 모드에서만 신규 진입 수행
                if mode == "TRADE":
                    raw_signals = generate_signals(candidates, self.paths["STRATEGY"])
                    
                    # 4. 리스크 게이트 (시스템 설정 주입)
                    approved_signals = []
                    for sig in raw_signals:
                        # [FIX] 주입 동기화: strategy_path 대신 system_config 전달
                        res = validate_risk_and_size(sig, self.current_state, self.system_config)
                        
                        if res.get("allowed"):
                            sig.update({
                                "volume": res.get("size"), 
                                "risk_reason": res.get("reason")
                            })
                            approved_signals.append(sig)

                    # 5. 주문 전 최종 검증 (모드 독립 차단 포함)
                    final_signals = validate_before_order(
                        approved_signals, 
                        mode, 
                        self.current_state.get("positions", []), 
                        self.system_config
                    )

                    # 6. 주문 실행 및 체결 추적
                    if final_signals:
                        self.guard.check() 
                        execution_results = execute_orders(final_signals)
                        
                        # [PHASE 4] 체결 후속 처리 (Fill -> Ledger)
                        fills = track_fills(execution_results)
                        # [FIX] ledger_writer 경로 오염 방지 (evidence_root 전달)
                        record_to_ledger(fills, evidence_root)
            
            # [PHASE 5] 청산 및 상태 동기화 (순서: Exit -> Reconcile)
            # 7. 청산 엔진 (전략 기반 익절/손절/강제청산 판단)
            # [FIX] 시그니처 일치: strategy_path 추가 전달
            exit_results = process_exits(mode, self.current_state, self.paths["STRATEGY"])

            # 8. 포지션 리컨실러 (상태 업데이트 및 물리 저장)
            # [FIX] 시그니처 일치: (state, results, path) 3인자 주입
            self.current_state = reconcile_positions(
                current_state=self.current_state, 
                exit_results=exit_results, 
                state_path=state_file_path
            )           
            
            self.guard.check() # 최종 무결성 확인
            logger.info(f"CYCLE_COMPLETE: Mode={mode} | Active Positions: {len(self.current_state.get('positions', []))}")

        except Exception as e:
            # [FIX] 정책 연계: error context와 paths(dict) 전달하여 정책 집행
            logger.error(f"RUNTIME_EXCEPTION: {str(e)}")
            handle_critical_error(str(e), self.paths)

if __name__ == "__main__":
    engine = IroncladEngine()
    engine.run()