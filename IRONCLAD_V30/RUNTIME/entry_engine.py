import logging
from typing import List, Dict, Any

logger = logging.getLogger("IRONCLAD_RUNTIME.ENTRY_ENGINE")


def filter_by_today_symbols(signals: List[Dict[str, Any]], state: Dict[str, Any]) -> List[Dict[str, Any]]:
    allowed_stock = set(state.get("symbols", {}).get("stock", []))
    allowed_crypto = set(state.get("symbols", {}).get("crypto", []))

    filtered = []

    for sig in signals:
        symbol = sig.get("symbol")
        asset_type = sig.get("asset_type")  # "STOCK" or "CRYPTO"

        if asset_type == "STOCK" and symbol in allowed_stock:
            filtered.append(sig)

        elif asset_type == "CRYPTO" and symbol in allowed_crypto:
            filtered.append(sig)

    return filtered


def generate_signals(
    candidates: List[Dict[str, Any]],
    strategy_path: str,
    state: Dict[str, Any]  # ✅ 추가
) -> List[Dict[str, Any]]:

    if not candidates:
        return []

    try:
        signals = []

        for asset in candidates:
            signals.append({
                "symbol": asset.get("symbol"),
                "side": "BUY",
                "price": asset.get("price"),
                "asset_type": asset.get("asset_type"),
                "entry_score": asset.get("selection_score", 0)
            })

        # ✅ 오늘 종목만 필터
        signals = filter_by_today_symbols(signals, state)

        logger.info(f"ENTRY_ENGINE: Filtered {len(signals)} signals (today symbols only).")

        return signals

    except Exception as e:
        raise RuntimeError(f"ENTRY_ENGINE_FAILURE: {str(e)}")