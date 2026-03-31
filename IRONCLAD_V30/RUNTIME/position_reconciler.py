# position_reconciler.py

import logging

logger = logging.getLogger("IRONCLAD_RECONCILER")


def reconcile_positions(state, exit_results, state_path):
    """
    입력:
        state: dict
        exit_results: dict
    출력:
        dict
    """

    # =========================
    # 🔵 입력 방어 (핵심)
    # =========================
    if not isinstance(state, dict):
        return {"positions": {}}

    positions = state.get("positions", {})

    if not isinstance(positions, dict):
        positions = {}

    # exit_results 방어
    if isinstance(exit_results, list):
        # 잘못 들어온 경우 무시
        exit_results = {}

    if not isinstance(exit_results, dict):
        exit_results = {}

    # =========================
    # 🔵 안전 복사
    # =========================
    new_positions = {}

    for symbol, pos in positions.items():

        # 🔴 여기서 기존 코드가 터졌을 가능성 높음
        if not isinstance(symbol, str):
            continue

        if not isinstance(pos, dict):
            continue

        # =========================
        # 🔵 EXIT 처리 (현재 없음)
        # =========================
        if symbol in exit_results:
            continue

        new_positions[symbol] = pos

    # =========================
    # 🔵 상태 업데이트
    # =========================
    state["positions"] = new_positions

    return state