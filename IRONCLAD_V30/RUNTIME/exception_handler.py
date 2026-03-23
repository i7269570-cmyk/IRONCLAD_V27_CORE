import yaml
import sys
import logging

logger = logging.getLogger("IRONCLAD_RUNTIME.EXCEPTION_HANDLER")

def handle_critical_error(error_context: str, paths: dict):
    """
    [FIX] 하드코딩 폴백 제거: 정책 로드 실패 시 임의 판단 없이 즉시 종료한다.
    """
    logger.critical(f"SAFE_HALT_TRIGGERED: {error_context}")
    
    try:
        # 정책 파일 직접 참조
        with open(paths["RECOVERY_POLICY"], 'r', encoding='utf-8') as f:
            policy_data = yaml.safe_load(f)
            if not policy_data: raise ValueError("EMPTY_POLICY_FILE")
            
            policy = policy_data.get("recovery_policy", {})
        
        # [FIX] 정책 데이터가 없거나 로드 실패 시 하드코딩된 변수 사용 금지
        allow_recovery = policy["allow_recovery"]
        restart_required = policy["restart_required"]

        if not allow_recovery and restart_required:
            logger.info("POLICY_ENFORCED: Auto-recovery disabled. Process terminated.")
            sys.exit(1)
            
    except Exception as e:
        # 정책을 확인할 수 없는 상태는 가장 위험한 상태이므로 즉시 강제 종료
        logger.error(f"HANDLER_FATAL: Recovery policy unreachable or malformed. {str(e)}")
        sys.exit(1)