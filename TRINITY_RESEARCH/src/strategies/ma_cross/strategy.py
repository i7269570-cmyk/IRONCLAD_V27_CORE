class MACrossStrategy:

    def on_bar(self, row, position):
        if position is not None:
            return None

        try:
            # 5일 이평이 20일 이평 상향 돌파 + 거래량 폭발
            if (row["ma5"] > row["ma20"] and 
                row["ma5"].shift(1) <= row["ma20"].shift(1) and
                row["volume"] > row["volume_ma"] * 1.8):
                return "BUY"
        except:
            return None

        return None


    def on_position(self, row, position):
        entry = position["entry_price"]
        current = row["close"]
        bars_held = position["bars_held"]

        pnl = (current - entry) / entry

        if pnl >= 0.006 or pnl <= -0.005 or bars_held >= 12:
            return "EXIT"

        return None