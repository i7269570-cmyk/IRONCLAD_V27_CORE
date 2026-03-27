import os
import yaml
import pandas as pd
import logging
from typing import List, Dict, Any

logger = logging.getLogger("IRONCLAD_V30.DATA_LOADER")

def load_market_data(asset_types: List[str], strategy_path: str) -> List[Dict[str, Any]]:
    """[V30_FINAL] 조용한 실패 방지 및 경로 SSOT 통합 완료."""
    try:
        # 1. 설정 로드 (SSOT)
        rules_file = os.path.join(strategy_path, "data_rules.yaml")
        with open(rules_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 2. [교정] RISK 해결: 실행 위치 독립적인 경로 산출 (데이터 폴더 고정) [cite: 2026-03-28]
        # strategy_path를 기준으로 한 단계 상위의 data 폴더를 참조하도록 통합
        csv_path = os.path.normpath(os.path.join(strategy_path, "..", "..", "data", "target_300.csv"))
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"TARGET_CSV_MISSING: {csv_path}")

        # 3. 데이터 로드 및 필터링
        df = pd.read_csv(csv_path)
        default_type = config.get('default_asset_type', 'STOCK')
        df['asset_type'] = default_type
        
        # [교정] FAIL 해결: 공집합 시 조용한 실패 방지 [cite: 2026-03-28]
        allow_list = config.get('allow_assets', [])
        valid_types = [t for t in asset_types if t in allow_list]
        
        if not valid_types:
            error_msg = f"VALIDATION_ERROR: Requested {asset_types} not in allowed {allow_list}"
            logger.error(error_msg)
            raise ValueError(error_msg) # 조용히 넘기지 않고 에러 발생 [cite: 2026-03-28]

        df = df[df['asset_type'].isin(valid_types)]
        
        # 4. 데이터 규격 변환
        df = df.rename(columns={'종목명': 'symbol', '현재가': 'price', '거래대금': 'value', '등락률': 'change_rate'})
        df['change_rate'] = df['change_rate'].astype(str).str.replace('%', '').str.replace('+', '').astype(float)
        
        return df.head(config.get('top_n_limit', 50)).to_dict('records')

    except Exception as e:
        logger.error(f"LOADER_CRITICAL: {e}")
        raise RuntimeError(e)