class MomentumVolumeBreakoutStrategy:

    TAKE_PROFIT = 0.012   # 빠른 익절
    STOP_LOSS   = 0.012   # 리스크 동일
    MAX_HOLD    = 4

    def on_bar(self, row, position):

        if position is not None:
            return None

        try:
            # --- 추세 완화
            if row['close'] < row['ma20'] * 0.95:
                return None

            # --- 과매도 완화
            if row['rsi'] <= 40 and row['close'] <= row['bb_lower']:

                # --- 반등 완화
                if row['close'] > (row['low'] * 1.003):
                    return "BUY"

        except:
            return None

        return None


    def on_position(self, row, position):

        if position is None:
            return None

        try:
            pnl = (row["close"] - position["entry_price"]) / position["entry_price"]
            hold = position.get("hold_bars", 0)

            if row['close'] >= row['bb_middle']:
                return "EXIT"

            if pnl >= self.TAKE_PROFIT:
                return "EXIT"

            if pnl <= -self.STOP_LOSS:
                return "EXIT"

            if hold >= self.MAX_HOLD:
                return "EXIT"

            position["hold_bars"] = hold + 1

        except:
            return None

        return None