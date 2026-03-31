# ============================================================
# IRONCLAD_V27 - Rapid Profit Capture (V40_FIXED)
# ============================================================

class VolatilityBreakout_A:
    """ A: 타점 K=0.4 + 변동성+거래량 진입 / 익절 미달 즉시 청산 """
    K_VALUE      = 0.40      
    VOL_FILTER   = 3.0       
    TAKE_PROFIT  = 0.03
    STOP_LOSS    = 0.015
    MAX_HOLD     = 2

    def on_bar(self, row, position):
        if position is not None: return None
        try:
            target = row['open'] + ((row['high_prev'] - row['low_prev']) * self.K_VALUE)
            if row['close'] > target and row['close'] > row['ma60']:
                if row['volume'] > row['v_ma20'] * self.VOL_FILTER:
                    return "BUY"
        except: return None
        return None

    def on_position(self, row, position):
        pnl = (row["close"] - position["entry_price"]) / position["entry_price"]
        hold = position.get("hold_bars", 0)
        # 변경: 익절 달성 or 손절 or 1바 후 수익 미달이면 즉시 청산
        if pnl >= self.TAKE_PROFIT or pnl <= -self.STOP_LOSS or hold >= 1:
            return "EXIT"
        position["hold_bars"] = hold + 1
        return None


class VolatilityBreakout_B:
    """ B: 타점 K=0.4 + 1바 즉시 승부 (원본 유지) """
    K_VALUE      = 0.40      
    VOL_FILTER   = 3.0       
    TAKE_PROFIT  = 0.05      
    STOP_LOSS    = 0.01      
    MAX_HOLD     = 1

    def on_bar(self, row, position):
        if position is not None: return None
        try:
            target = row['open'] + ((row['high_prev'] - row['low_prev']) * self.K_VALUE)
            if row['close'] > target and row['close'] > row['ma60']:
                if row['volume'] > row['v_ma20'] * self.VOL_FILTER:
                    return "BUY"
        except: return None
        return None

    def on_position(self, row, position):
        pnl = (row["close"] - position["entry_price"]) / position["entry_price"]
        hold = position.get("hold_bars", 0)
        if pnl > 0.01 or pnl <= -self.STOP_LOSS or hold >= self.MAX_HOLD:
            return "EXIT"
        position["hold_bars"] = hold + 1
        return None


class VolatilityBreakout_C:
    """ C: 폐기 대상 - 구조 유지용 더미 """
    K_VALUE      = 0.30      
    VOL_FILTER   = 3.0       
    TAKE_PROFIT  = 0.05      
    STOP_LOSS    = 0.01      
    MAX_HOLD     = 1

    def on_bar(self, row, position):
        if position is not None: return None
        try:
            target = row['open'] + ((row['high_prev'] - row['low_prev']) * self.K_VALUE)
            if row['close'] > target and row['close'] > row['ma60']:
                if row['volume'] > row['v_ma20'] * self.VOL_FILTER:
                    return "BUY"
        except: return None
        return None

    def on_position(self, row, position):
        pnl = (row["close"] - position["entry_price"]) / position["entry_price"]
        hold = position.get("hold_bars", 0)
        if pnl > 0.01 or pnl <= -self.STOP_LOSS or hold >= self.MAX_HOLD:
            return "EXIT"
        position["hold_bars"] = hold + 1
        return None