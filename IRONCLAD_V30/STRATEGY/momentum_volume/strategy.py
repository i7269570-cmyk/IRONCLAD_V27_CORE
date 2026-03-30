class MomentumVolumeBreakoutStrategy:

    def on_bar(self, row, position):
        if position is not None:
            return None
        return "BUY"

    def on_position(self, row, position):
        return None