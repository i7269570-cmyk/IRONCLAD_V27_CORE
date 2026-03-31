# risk_gate.py

def validate_risk_and_size(signal, state, system_config):
    """
    입력: dict
    출력: dict
    """

    # =========================
    # 🔵 입력 방어 (핵심)
    # =========================
    if not isinstance(signal, dict):
        return {"allowed": False}

    if not isinstance(state, dict):
        return {"allowed": False}

    if not isinstance(system_config, dict):
        system_config = {}

    symbol = signal.get("symbol")
    price = signal.get("price")
    asset_type = signal.get("asset_type")

    if not symbol or price is None:
        return {"allowed": False}

    # =========================
    # 🔵 기본 자금 계산
    # =========================
    capital = state.get("capital", {})

    if not isinstance(capital, dict):
        return {"allowed": False}

    total = capital.get("total", 0)

    if total <= 0:
        return {"allowed": False}

    # =========================
    # 🔵 간단 사이징 (안전)
    # =========================
    try:
        size = total * 0.01  # 1% 고정
    except Exception:
        return {"allowed": False}

    # =========================
    # 🔵 최종 반환 (형식 고정)
    # =========================
    return {
        "allowed": True,
        "size": size
    }