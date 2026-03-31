# fill_tracker.py

import logging

logger = logging.getLogger("IRONCLAD_FILL_TRACKER")


def track_fills(order_results, state):
    """
    입력: list[dict]
    출력: list[dict]
    """

    if isinstance(order_results, dict):
        order_results = [order_results]

    if not isinstance(order_results, list):
        raise TypeError(f"order_results must be list, got {type(order_results)}")

    fills = []

    for o in order_results:
        if not isinstance(o, dict):
            continue

        if o.get("status") != "FILLED":
            continue

        fills.append({
            "symbol": o.get("symbol"),
            "side": o.get("side"),
            "price": o.get("price"),
            "asset_type": o.get("asset_type")
        })

    logger.info(f"FILL_TRACKER_SUCCESS: {len(fills)} fills")

    return fills