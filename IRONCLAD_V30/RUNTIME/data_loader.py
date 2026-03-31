import os
import yaml
import pandas as pd
import logging
from typing import List, Dict, Any

logger = logging.getLogger("IRONCLAD_V30.DATA_LOADER")

def load_market_data(asset_types: List[str], strategy_path: str) -> List[Dict[str, Any]]:
    try:
        # 설정 로드
        rules_file = os.path.join(strategy_path, "data_rules.yaml")
        with open(rules_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # default 존재 강제
        if 'default_asset_type' not in config:
            raise ValueError("MISSING_default_asset_type")

        # CSV 경로
        # CSV 경로 (수정)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(BASE_DIR, "data", "target_100.csv")

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"TARGET_CSV_MISSING: {csv_path}")
  
        df = pd.read_csv(csv_path)

        # ⭐ 컬럼 검증 (고정 4개만)
        required_cols = ['symbol', 'price', 'value', 'change_rate']
        missing = [c for c in required_cols if c not in df.columns]

        if missing:
            raise ValueError(f"MISSING_COLUMNS: {missing}")

        # 타입 정리
        df['change_rate'] = (
            df['change_rate']
            .astype(str)
            .str.replace('%', '', regex=False)
            .str.replace('+', '', regex=False)
            .astype(float)
        )

        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['value'] = pd.to_numeric(df['value'], errors='coerce')

        df = df.dropna(subset=['symbol', 'price', 'value', 'change_rate'])

        logger.info(f"DATA_LOADER_SUCCESS: loaded {len(df)} assets")

        return df.to_dict('records')

    except Exception as e:
        logger.error(f"LOADER_CRITICAL: {e}")
        raise RuntimeError(e)