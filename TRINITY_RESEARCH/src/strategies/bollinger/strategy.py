class BollingerStrategy:

    def on_bar(self, row, position):
        if position is not None:
            return None

        try:
            # 볼린저 상단 돌파 + 거래량 확인 + 이평 위
            if (row["close"] > row["bb_upper"] and 
                row["volume"] > row["volume_ma"] * 1.8 and
                row["close"] > row["ma20"]):
                return "BUY"
        except:
            return None

        return None


    def on_position(self, row, position):
        entry = position["entry_price"]
        current = row["close"]
        bars_held = position["bars_held"]

        pnl = (current - entry) / entry

        if pnl >= 0.006 or pnl <= -0.005 or bars_held >= 10:
            return "EXIT"

        return None