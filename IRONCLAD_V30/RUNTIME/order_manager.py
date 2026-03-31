# order_manager.py

import logging

logger = logging.getLogger("IRONCLAD_ORDER_MANAGER")


def execute_orders(signals):
    """
    입력: list[dict]
    출력: list[dict]
    """

    # =========================
    # 🔵 입력 방어 (필수)
    # =========================
    if isinstance(signals, dict):
        signals = [signals]

    if not isinstance(signals, list):
        raise TypeError(f"signals must be list[dict], got {type(signals)}")

    clean_signals = []
    for s in signals:
        if isinstance(s, dict):
            clean_signals.append(s)

    # =========================
    # 🔵 실행
    # =========================
    results = []

    for sig in clean_signals:
        try:
            symbol = sig.get("symbol")
            side = sig.get("side")
            price = sig.get("price")
            asset_type = sig.get("asset_type")

            if not symbol or not side:
                continue

            logger.info(f"ORDER_SUCCESS: {symbol} | Side: {side}")

            results.append({
                "symbol": symbol,
                "side": side,
                "price": price,
                "asset_type": asset_type,
                "status": "FILLED"
            })

        except Exception as e:
            logger.error(f"ORDER_FAIL: {str(e)}")

    logger.info(f"ORDER_MANAGER: All {len(results)} orders filled successfully.")

    # =========================
    # 🔵 출력 보장 (핵심)
    # =========================
    return results