strategy_name: VOL_BREAKOUT_BALANCED_V1

description: >
  Volume Breakout 기반 단기 모멘텀 전략.
  중간 강도의 거래량 증가 조건에서 진입하여
  짧은 수익을 반복적으로 확보하는 구조.

data_requirements:
  - price (OHLC)
  - volume
  - avg_volume_20

entry_condition:
  breakout:
    condition: "close > rolling_high_20"
  volume:
    condition: "volume > avg_volume_20 * 1.3"

execution:
  entry: "next_open"
  position_type: "long"

exit_condition:
  take_profit_pct: 0.02
  stop_loss_pct: -0.015
  max_holding_bars: 5
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