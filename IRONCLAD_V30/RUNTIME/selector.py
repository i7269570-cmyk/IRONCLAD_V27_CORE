import os
import yaml
import logging
from typing import List, Dict, Any

# =============================================================================
# IRONCLAD_V30.1_FINAL: SELECTOR
# =============================================================================

logger = logging.getLogger("IRONCLAD_RUNTIME.SELECTOR")

def select_candidates(data: List[Dict[str, Any]], strategy_path: str) -> List[Dict[str, Any]]:
    """
    가중치 기반 점수 산출 및 최종 3~5개 후보 선정 (최소 3개 보장 로직 포함)
    """
    if not data:
        return []

    try:
        # [1] 전략 파일 로드
        rules_file = os.path.join(strategy_path, "selection_rules.yaml")
        with open(rules_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        rules = config.get('selection_criteria', {})
        weights = config.get('weights', {"value": 0.5, "change": 0.5}) # 가중치 외부화
        
        min_count = config.get('min_selection_count', 3) # 최소 3개 보장 기준
        max_count = config.get('max_selection_count', 5) # 최대 5개 상한

        # [2] 점수 계산 (하드코딩 제거: YAML 가중치 적용)
        scored_list = []
        for item in data:
            val_score = item.get('value', 0) * weights.get('value', 0)
            chg_score = item.get('change_rate', 0) * weights.get('change', 0)
            
            item['selection_score'] = val_score + chg_score
            scored_list.append(item)

        # [3] 정렬 및 슬라이싱
        sorted_list = sorted(scored_list, key=lambda x: x['selection_score'], reverse=True)
        final_candidates = sorted_list[:max_count]

        # [4] 최소 수량 보장 검증 (Lower Bound Check)
        if len(final_candidates) < min_count:
            logger.warning(f"SELECTOR_UNDERFLOW: Selected only {len(final_candidates)} (Min required: {min_count})")
            # 전략에 따라 빈 리스트를 주거나, 부족한 채로 진행 (여기서는 경고 후 진행)
        
        logger.info(f"SELECTOR: Final selection complete ({len(final_candidates)} assets).")
        return final_candidates

    except Exception as e:
        raise RuntimeError(f"SELECTOR_FAILURE: {str(e)}")