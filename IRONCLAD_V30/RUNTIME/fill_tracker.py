import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger("IRONCLAD_RUNTIME.FILL_TRACKER")


def track_fills(
    orders: List[Dict[str, Any]],
    state: Dict[str, Any]   # ✅ state 연결
) -> List[Dict[str, Any]]:

    processed_fills = []

    for order in orders:
        status = order.get("status", "FAILED").upper()

        if status in ["FILLED", "PARTIAL"]:
            price = order.get("executed_price") or order.get("avg_price")
            volume = order.get("executed_volume") or order.get("filled_qty")

            if price is None or volume is None or price <= 0 or volume <= 0:
                error_msg = f"FILL_TRACKER_CRITICAL: Malformed data for {order.get('symbol')}"
                logger.critical(error_msg)
                raise RuntimeError(error_msg)

            symbol = order.get("symbol")
            asset_type = order.get("asset_type")
            side = order.get("side", "BUY")

            now = datetime.utcnow().isoformat()

            # =========================
            # 1. 포지션 반영 (BUY 기준)
            # =========================
            if side == "BUY":
                state.setdefault("positions", {})

                state["positions"][symbol] = {
                    "symbol": symbol,
                    "asset_type": asset_type,
                    "entry_price": price,
                    "size": volume,
                    "entry_time": now
                }

                # =========================
                # 2. 자금 차감
                # =========================
                cost = price * volume

                if asset_type == "STOCK":
                    state["capital"]["stock_alloc"] -= cost
                else:
                    state["capital"]["crypto_alloc"] -= cost

            # =========================
            # 3. 기록
            # =========================
            processed_fills.append({
                "symbol": symbol,
                "status": status,
                "filled_price": price,
                "filled_size": volume,
                "side": side
            })

    return processed_fills