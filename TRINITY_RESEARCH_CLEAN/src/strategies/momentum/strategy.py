class MomentumStrategy:

    def on_bar(self, row, position):

        if position is not None:
            return None

        try:
            volume = row["volume"]
            volume_ma = row["volume_ma"]

            if volume_ma == 0:
                return None

            volume_ratio = volume / volume_ma

        except:
            return None

        if volume_ratio >= 1.45:
            return "BUY"

        return None


    def on_position(self, row, position):

        entry = position["entry_price"]
        current = row["close"]

        pnl = (current - entry) / entry

        if pnl >= 0.003:
            return "EXIT"

        if pnl <= -0.005:
            return "EXIT"

        if position["bars_held"] >= 5:
            return "EXIT"

        return None