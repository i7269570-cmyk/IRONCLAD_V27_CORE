import os
import yaml
import logging
from typing import List, Dict, Any

# =============================================================================
# IRONCLAD_V30.1_FINAL: REGIME_FILTER
# =============================================================================

logger = logging.getLogger("IRONCLAD_RUNTIME.REGIME_FILTER")

def evaluate_market_regime(market_data: List[Dict[str, Any]], strategy_path: str) -> bool:
    """
    시장 추세 및 변동성을 확인하여 GO/NO-GO 결정.
    """
    try:
        rules_file = os.path.join(strategy_path, "regime_rules.yaml")
        with open(rules_file, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f).get('market_regime', {})

        # 전략 기반 임계치
        min_trend = rules.get('min_trend_score', 50)
        
        # 현재 시장 평균 추세 계산 (Mock)
        avg_trend = sum(item.get('trend_score', 60) for item in market_data) / len(market_data) if market_data else 0

        if avg_trend >= min_trend:
            logger.info(f"REGIME_FILTER: PASS (Score: {avg_trend})")
            return True
        
        logger.warning(f"REGIME_FILTER: REJECT (Score: {avg_trend} < {min_trend})")
        return False

    except Exception as e:
        raise RuntimeError(f"REGIME_FILTER_FAILURE: {str(e)}")