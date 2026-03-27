import os
import yaml
import logging
from typing import List, Dict, Any

logger = logging.getLogger("IRONCLAD_RUNTIME.SELECTOR")

def select_candidates(data: List[Dict[str, Any]], strategy_path: str) -> List[Dict[str, Any]]:
    """
    Top 50 종목 선정:
    - 거래대금 + 상승률 기반 점수
    - 정확히 50개 반환
    """

    if not data:
        return []

    try:
        rules_file = os.path.join(strategy_path, "selection_rules.yaml")

        with open(rules_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if not config:
            raise ValueError("EMPTY_SELECTION_RULES")

        if 'weights' not in config:
            raise ValueError("MISSING_weights")

        weights = config['weights']

        required_weight_keys = ['value', 'change_rate']
        missing_weight_keys = [k for k in required_weight_keys if k not in weights]
        if missing_weight_keys:
            raise ValueError(f"MISSING_WEIGHT_KEYS: {missing_weight_keys}")

        scored_list = []

        for item in data:
            if 'value' not in item or 'change_rate' not in item:
                raise ValueError("MISSING_ITEM_KEYS")

            val_score = item['value'] * weights['value']
            chg_score = item['change_rate'] * weights['change_rate']

            scored_item = dict(item)
            scored_item['selection_score'] = val_score + chg_score
            scored_list.append(scored_item)

        sorted_list = sorted(
            scored_list,
            key=lambda x: x['selection_score'],
            reverse=True
        )

        final_candidates = sorted_list[:50]

        logger.info(f"SELECTOR: Final selection complete ({len(final_candidates)} assets).")

        return final_candidates

    except Exception as e:
        raise RuntimeError(f"SELECTOR_FAILURE: {str(e)}")