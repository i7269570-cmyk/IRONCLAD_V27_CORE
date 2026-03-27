import os
import yaml
import pandas as pd

def filter_by_strategy(market_data: list, strategy_path: str):
    """[V30_FINAL] YAML 연계 무효 리스크 해결 완료."""
    
    spec_file = os.path.join(strategy_path, "strategy_spec.yaml")
    with open(spec_file, 'r', encoding='utf-8') as f:
        spec = yaml.safe_load(f)
    
    strat_conf = spec.get('strategy', {})
    univ_conf = strat_conf.get('universe', {})
    
    # [교정] RISK 해결: YAML 키 경로 일치 (entry_condition 내부 접근) [cite: 2026-03-28]
    # 이제 YAML에서 3.0을 5.0으로 바꾸면 즉시 반영됩니다.
    entry_cond = strat_conf.get('entry_condition', {})
    min_change = entry_cond.get('min_change_rate', 3.0) 
    top_n = univ_conf.get('top_n', 50)
    
    df = pd.DataFrame(market_data)
    candidates = df.nlargest(top_n, 'value')
    return candidates[candidates['change_rate'] >= min_change].to_dict('records')