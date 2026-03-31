import logging
import os
import yaml
from typing import List, Dict, Any

logger = logging.getLogger("IRONCLAD_RUNTIME.ENTRY_ENGINE")


# =========================
# 🔵 전략 로드 (수정 금지)
# =========================
def load_strategy(strategy_path: str, asset_type: str) -> Dict[str, Any]:
    file_name = "stock_strategy.yaml" if asset_type == "STOCK" else "crypto_strategy.yaml"
    path = os.path.join(strategy_path, file_name)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def generate_signals(
    candidates: List[Dict[str, Any]],
    strategy_path: str,
    state: Dict[str, Any]
) -> List[Dict[str, Any]]:

    # =========================
    # 🔵 입력 방어
    # =========================
    if isinstance(candidates, dict):
        candidates = [candidates]

    if not isinstance(candidates, list):
        return []

    if not candidates:
        print("ENTRY_ENGINE: candidates 비어있음")
        return []

    try:
        print("===== ENTRY_ENGINE START =====")
        print("CANDIDATE COUNT:", len(candidates))

        valid_candidates = [c for c in candidates if isinstance(c, dict)]

        if not valid_candidates:
            print("유효한 candidate 없음")
            return []

        print("FIRST VALID:", valid_candidates[0])

        required_fields = ["symbol", "asset_type", "price"]

        missing = [f for f in required_fields if f not in valid_candidates[0]]
        if missing:
            print("MISSING FIELDS:", missing)
        else:
            print("BASIC FIELDS OK")

        signals: List[Dict[str, Any]] = []

        stock_count = 0
        crypto_count = 0

        for asset in valid_candidates:

            symbol = asset.get("symbol")
            price = asset.get("price")
            asset_type = asset.get("asset_type")

            if not symbol or price is None or not asset_type:
                continue

            # =========================
            # 🔥 전략 로드
            # =========================
            strategy = load_strategy(strategy_path, asset_type)
            entry = strategy.get("entry", {})

            rsi_max = entry.get("rsi_max")
            bb_mul = entry.get("bb_multiplier")
            low_buf = entry.get("low_buffer")

            # =========================
            # 🔥 전략 조건
            # =========================
            allow_entry = False

            if (
                asset.get("rsi") is not None and
                asset.get("bb_lower") is not None and
                asset.get("low") is not None and

                rsi_max is not None and
                bb_mul is not None and
                low_buf is not None
            ):
                if (
                    asset["rsi"] < rsi_max and
                    asset["price"] <= asset["bb_lower"] * bb_mul and
                    asset["price"] > asset["low"] * low_buf
                ):
                    allow_entry = True

            if not allow_entry:
                continue

            # =========================
            # 🔵 종목 제한
            # =========================
            if asset_type == "STOCK":
                if stock_count >= 2:
                    continue
                stock_count += 1

            elif asset_type == "CRYPTO":
                if crypto_count >= 2:
                    continue
                crypto_count += 1

            signals.append({
                "symbol": symbol,
                "side": "BUY",
                "price": price,
                "asset_type": asset_type,
            })

        # =========================
        # 🔵 출력 정규화
        # =========================
        clean_signals = [s for s in signals if isinstance(s, dict)]

        print("FINAL SIGNALS:", clean_signals)
        print("===== ENTRY_ENGINE END =====")

        return clean_signals

    except Exception as e:
        raise RuntimeError(f"ENTRY_ENGINE_FAILURE: {str(e)}")