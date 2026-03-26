class MeanReversionBBStrategy:
    TAKE_PROFIT = 0.015   # 목표 수익 1.5%
    STOP_LOSS   = 0.010   # 손절 1.0%
    MAX_HOLD    = 5       # 반등은 빠르게 종료

    def on_bar(self, row, position):
        if position is not None: return None
        try:
            # 1. 검증된 과매도 필터: RSI 35 미만 & BB 하단 이탈
            if row['rsi'] < 35 and row['close'] < row['bb_lower']:
                # 2. 반등 확인: 저점 대비 0.5% 반등 시 정밀 진입
                if row['close'] > (row['low'] * 1.005):
                    return "BUY"
        except: return None
        return None

    def on_position(self, row, position):
        if position is None: return None
        try:
            pnl = (row["close"] - position["entry_price"]) / position["entry_price"]
            
            # [추가] 강화된 익절 로직: BB 중앙선 도달 시 또는 0.8% 수익 후 음봉 시 탈출
            if row['close'] >= row['bb_middle'] or (pnl >= 0.008 and row['close'] < row['open']):
                return "EXIT"

            if pnl >= self.TAKE_PROFIT or pnl <= -self.STOP_LOSS or position.get("hold_bars", 0) >= self.MAX_HOLD:
                return "EXIT"
            
            position["hold_bars"] = position.get("hold_bars", 0) + 1
        except: return None
        return None