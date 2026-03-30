class MeanReversionBBStrategy:

    TAKE_PROFIT = 0.015
    STOP_LOSS = 0.01
    MAX_HOLD = 5

    def on_bar(self, row, position):
        if position is not None:
            return None

        # RSI 조건
        if row['rsi'] > 45:
            return None

        # BB 하단
        if row['close'] > row['bb_lower'] * 1.01:
            return None

        # 반등 확인
        if row['close'] <= row['low'] * 1.005:
            return None

        return "BUY"

    def on_position(self, row, position):
        if position is None:
            return None

        pnl = (row["close"] - position["entry_price"]) / position["entry_price"]
        hold = position.get("hold_bars", 0)

        # BB 중단
        if row['close'] >= row['bb_middle']:
            return "EXIT"

        # TP
        if pnl >= self.TAKE_PROFIT:
            return "EXIT"

        # SL
        if pnl <= -self.STOP_LOSS:
            return "EXIT"

        # 시간
        if hold >= self.MAX_HOLD:
            return "EXIT"

        position["hold_bars"] = hold + 1

        return None