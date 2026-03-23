strategy_name: VOL_BREAKOUT_CONSERVATIVE_V1

description: >
  Volume Breakout 기반 보수형 단타 전략.
  거래량 조건을 강화하여 노이즈를 줄이고
  안정적인 수익을 목표로 하는 구조.

data_requirements:
  - price (OHLC)
  - volume
  - avg_volume_20

entry_condition:
  breakout:
    condition: "close > rolling_high_20"
  volume:
    condition: "volume > avg_volume_20 * 1.4"

execution:
  entry: "next_open"
  position_type: "long"

exit_condition:
  take_profit_pct: 0.015
  stop_loss_pct: -0.01
  max_holding_bars: 7
  trailing_stop: false

risk_management:
  max_consecutive_loss: 3

position:
  max_position_per_trade: 1.0

validation:
  min_trades: 30
  reject_if:
    - "total_return <= 0"

metadata:
  created_at: "2026-03-18"
  version: "V1"
  status: "locked"