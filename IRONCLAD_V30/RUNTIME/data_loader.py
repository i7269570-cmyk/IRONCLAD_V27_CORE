import os
import yaml
from typing import List, Dict, Any

def load_market_data(asset_types: List[str], strategy_path: str) -> List[Dict[str, Any]]:
    """[RISK 해결] 기본값 자동 생성 없이 설정 파일의 키를 강제 로드한다."""
    try:
        rules_file = os.path.join(strategy_path, "data_rules.yaml")
        with open(rules_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 기본값 40 대신 KeyError 유도 (설정 파일 누락 방지)
        if 'top_n_limit' not in config:
            raise KeyError("DATA_LOADER_FAIL: 'top_n_limit' key missing in data_rules.yaml")
            
        limit_n = config['top_n_limit'] 
        
        # ... 데이터 로드 로직 (중략) ...
        return [] 
    except Exception as e:
        raise RuntimeError(f"DATA_LOADER_FAILURE: {e}")