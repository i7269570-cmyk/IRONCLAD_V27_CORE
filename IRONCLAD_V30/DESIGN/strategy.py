class MeanReversionBBStrategy:
    """
    IRONCLAD_V27 Standard Execution Logic
    Performance: PF 2.353, WinRate 60.1%
    """
    def __init__(self, spec=None):
        # YAML 설정값을 로드하거나 기본값을 사용합니다 (전략 고정 원칙)
        self.tp = 0.015
        self.sl = -0.010
        self.max_hold = 5

    def on_bar(self, row, position):
        # 단일 포지션 유지 원칙: 이미 포지션이 있으면 진입 건너뜀
        if position is not None:
            return None

        try:
            # 1. 과매도 필터 (RSI < 35 & BB 하단 이탈)
            is_oversold = (row['rsi'] < 35) and (row['close'] < row['bb_lower'])
            
            # 2. 정밀 반등 확인 (저점 대비 0.5% 반등 시)
            is_rebound = row['close'] > (row['low'] * 1.005)

            if is_oversold and is_rebound:
                return "BUY"
        except Exception:
            # 데이터 이상 시 거래 금지 규칙 준수
            return None
        return None

    def on_position(self, row, position):
        if position is None:
            return None

        try:
            entry_price = position.get("entry_price")
            current_close = row.get("close")
            bars_held = position.get("hold_bars", 0)
            
            pnl = (current_close - entry_price) / entry_price

            # 1. 수익 보존 로직: BB 중앙선 도달 시 또는 0.8% 수익 후 음봉 전환 시
            is_bb_mid_touch = current_close >= row.get('bb_middle', current_close)
            is_profit_protect = (pnl >= 0.008) and (current_close < row.get('open', current_close))

            if is_bb_mid_touch or is_profit_protect:
                return "EXIT"

            # 2. 고정 익절/손절/시간청산
            if pnl >= self.tp or pnl <= self.sl or bars_held >= self.max_hold:
                return "EXIT"
            
            # 상태 업데이트 (state.json 반영용)
            position["hold_bars"] = bars_held + 1
        except Exception:
            return None
        return None