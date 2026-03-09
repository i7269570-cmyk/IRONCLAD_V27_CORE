# entry_engine.py
import sys
import yaml
from pathlib import Path

def safe_halt(reason: str):
    print(f"[SAFE_HALT][ENTRY_ENGINE] {reason}")
    sys.exit(1)

class EntryEngine:
    def __init__(self, config_path: str, contract_path: str):
        base_dir = Path(__file__).resolve().parent
        self.spec = self._load_yaml(base_dir / config_path)
        self.contract = self._load_yaml(base_dir / contract_path)

        # Zero-Default: "stages" 키 존재 여부 강제 확인 (기본값 {} 삽입 금지)
        if "stages" not in self.contract:
            safe_halt("CONTRACT_KEY_MISSING: stages")
        
        stages = self.contract["stages"]
        
        # Zero-Default: sid 및 on_fail 키 존재 여부 강제 확인
        for sid in ["S2", "S3", "S4", "S5", "S6", "S7", "S8"]:
            if sid not in stages:
                safe_halt(f"CONTRACT_STAGE_MISSING: {sid}")
            
            if "on_fail" not in stages[sid]:
                safe_halt(f"CONTRACT_ON_FAIL_MISSING: {sid}")
                
            if stages[sid]["on_fail"] != "SAFE_HALT":
                safe_halt(f"CONTRACT_VIOLATION: {sid} on_fail must be SAFE_HALT")

    def _load_yaml(self, path: Path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            safe_halt(f"CONFIG_LOAD_FAIL {path}: {e}")
            
        if data is None:
            safe_halt(f"CONFIG_EMPTY: {path}")
        return data

    def _require(self, coin, key):
        """필수 데이터 키 검증: 누락 시 SAFE_HALT"""
        if key not in coin:
            safe_halt(f"DATA_KEY_MISSING: {key}")
        return coin[key]

    def run(self, market_data: list):
        if not isinstance(market_data, list):
            safe_halt("S5_INPUT_DATA_TYPE_INVALID")

        # 1. Liquidity Filter
        min_vol = self.spec["universe_filters"]["min_daily_volume"]
        liquid = []
        for d in market_data:
            daily_vol = self._require(d, "daily_volume")
            if daily_vol >= min_vol:
                liquid.append(d)

        # 2. Volume Spike
        spike_ratio = self.spec["universe_filters"]["vol_spike_ratio"]
        spiking = []
        for coin in liquid:
            curr_vol = self._require(coin, "volume")
            avg_vol = self._require(coin, "v_5_avg")
            if curr_vol / avg_vol >= spike_ratio:
                spiking.append(coin)

        # 3. Volatility Expansion
        threshold = self.spec["universe_filters"]["vol_expansion_threshold"]
        expanded = []
        for coin in spiking:
            high = self._require(coin, "high")
            low = self._require(coin, "low")
            close = self._require(coin, "close")
            if (high - low) / close >= threshold:
                expanded.append(coin)

        # 4. Selection Logic
        ranking_key = self.spec["selection_logic"]["ranking_metric"]
        target = self.spec["selection_logic"]["target_count"]
        ranked = sorted(expanded, key=lambda x: self._require(x, ranking_key), reverse=True)
        selected = ranked[:target]

        # 5. Signal Generation (timestamp 필수 적용)
        signals = []
        for coin in selected:
            timestamp = self._require(coin, "timestamp")
            signals.append({
                "symbol": coin["symbol"],
                "action": "READY",
                "timestamp": timestamp
            })
        return signals