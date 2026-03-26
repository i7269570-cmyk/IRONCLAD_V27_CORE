class ORBStrategy:
    def on_bar(self, row, position):
        if position is not None:
            return None

        t = int(row.get("time", 0))

        # 09:00~09:10 Range 형성 중에는 진입 금지
        if 90000 <= t <= 91000:
            return None

        # 상단 돌파 + 거래량 확인
        if (row.get("close", 0) > row.get("orb_high", 0) and 
            row.get("volume", 0) > row.get("volume_ma", 0) * 1.8):
            return "BUY"

        return None

    def on_position(self, row, position):
        entry = position.get("entry_price", 0)
        current = row.get("close", 0)
        bars = position.get("bars_held", 0)

        pnl = (current - entry) / entry if entry != 0 else 0

        if pnl >= 0.006 or pnl <= -0.003 or bars >= 3:
            return "EXIT"

        return None