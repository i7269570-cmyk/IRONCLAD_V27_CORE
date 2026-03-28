class MeanReversionBBStrategy:
    TAKE_PROFIT = 0.015   # 목표 수익 1.5%
    STOP_LOSS   = 0.010   # 손절 1.0%
    MAX_HOLD    = 5       # 최대 보유 5봉

    def on_bar(self, row, position):
        if position is not None:
            return None

        try:
            # --- 1. 추세 필터 (필수 추가)
            if row['close'] < row['ma20'] * 0.97:
                return None

            # --- 2. 과매도 + BB 하단 (노이즈 제거)
            if row['rsi'] < 45 and row['close'] <= row['bb_lower'] * 1.01:

                # --- 3. 반등 확인 (핵심 유지)
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

            # --- 1순위: BB 중앙선 도달 (Mean Reversion 완료)
            if row['close'] >= row['bb_middle']:
                return "EXIT"

            # --- 2순위: 목표 수익 도달
            if pnl >= self.TAKE_PROFIT:
                return "EXIT"

            # --- 3순위: 시간 종료
            if hold >= self.MAX_HOLD:
                return "EXIT"

            # --- 4순위: 손절
            if pnl <= -self.STOP_LOSS:
                return "EXIT"

            # --- 보유 시간 증가
            position["hold_bars"] = hold + 1

        except:
            return None

        return None