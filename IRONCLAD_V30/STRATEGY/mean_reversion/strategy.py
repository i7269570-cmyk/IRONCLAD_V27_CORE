class MeanReversionBBStrategy:
    TAKE_PROFIT = 0.015
    STOP_LOSS   = 0.010
    MAX_HOLD    = 5

    def on_bar(self, row, position):
        if position is not None:
            return None

        try:
            # --- [추세 완화 필터]
            if row['close'] < row['ma20'] * 0.97:
                return None

            # --- [과매도 + BB 하단]
            if row['rsi'] <= 35 and row['close'] <= row['bb_lower'] * 0.995:

                # --- [반등 확인]
                if row['close'] > (row['low'] * 1.005):
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

            # --- [1] BB 중단 도달
            if row['close'] >= row['bb_middle']:
                return "EXIT"

            # --- [2] 목표 수익
            if pnl >= self.TAKE_PROFIT:
                return "EXIT"

            # --- [3] 시간 종료
            if hold >= self.MAX_HOLD:
                return "EXIT"

            # --- [4] 손절
            if pnl <= -self.STOP_LOSS:
                return "EXIT"

            # --- [보유 증가]
            position["hold_bars"] = hold + 1

        except:
            return None

        return None