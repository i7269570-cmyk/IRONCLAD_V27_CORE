class MomentumVolumeBreakoutStrategy:
    TAKE_PROFIT = 0.040   # 익절 폭 확대 (+4.0%)
    STOP_LOSS   = 0.007   # 손절 타이트하게 (-0.7%)
    MAX_HOLD    = 10

    def on_bar(self, row, position):
        if position is not None: return None
        try:
            # 필터 1: 완벽한 정배열 (종가 > ma5 > ma20)
            is_perfect_trend = row['close'] > row['ma5'] > row['ma20']
            
            # 필터 2: 전봉 고점 돌파 (Breakout)
            is_breakout = row['close'] > row.get('high_prev', row['open'] * 1.02)
            
            # 필터 3: 거래량이 평균의 5배 이상 폭발 (돈이 몰리는 대장주만)
            is_huge_vol = row['volume'] > (row['volume_ma'] * 5.0)

            if is_perfect_trend and is_breakout and is_huge_vol:
                return "BUY"
        except: return None
        return None

    def on_position(self, row, position):
        # (기존 수익 보존 로직 유지)
        if position is None: return None
        try:
            pnl = (row["close"] - position["entry_price"]) / position["entry_price"]
            if pnl >= self.TAKE_PROFIT or pnl <= -self.STOP_LOSS or position.get("hold_bars", 0) >= self.MAX_HOLD:
                return "EXIT"
            position["hold_bars"] = position.get("hold_bars", 0) + 1
        except: return None
        return None