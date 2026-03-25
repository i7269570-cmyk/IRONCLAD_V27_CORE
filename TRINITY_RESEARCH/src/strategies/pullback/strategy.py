class PullbackStrategy:

    def on_bar(self, row, position):

        if position is not None:
            return None

        close = row.get("close", 0)
        prev_close_1 = row.get("close_prev_1", 0)

        # 🔥 진입 (검증된 구조 유지)
        if close > prev_close_1 * 1.001:
            return "BUY"

        return None


    def on_position(self, row, position):

        entry = position.get("entry_price", 0)
        current = row.get("close", 0)

        pnl = (current - entry) / entry if entry != 0 else 0

        if pnl >= 0.003:
            return "EXIT"

        if pnl <= -0.004:
            return "EXIT"

        if position.get("bars_held", 0) >= 4:
            return "EXIT"

        return None