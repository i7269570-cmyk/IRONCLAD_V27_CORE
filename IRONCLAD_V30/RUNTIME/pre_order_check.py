# pre_order_check.py

def validate_before_order(signals, mode, positions, system_config):
    """
    입력: list[dict]
    출력: list[dict]
    """

    # =========================
    # 🔵 입력 방어 (핵심)
    # =========================
    if isinstance(signals, dict):
        signals = [signals]

    if not isinstance(signals, list):
        raise TypeError(f"signals must be list, got {type(signals)}")

    clean_signals = []
    for s in signals:
        if isinstance(s, dict):
            clean_signals.append(s)

    # =========================
    # 🔵 기본 통과 로직
    # =========================
    validated = []

    for sig in clean_signals:
        try:
            symbol = sig.get("symbol")
            side = sig.get("side")

            if not symbol or not side:
                continue

            # 🔥 중복 포지션 방지
            if symbol in positions:
                continue

            validated.append(sig)

        except Exception:
            continue

    return validated