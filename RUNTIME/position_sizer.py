import sys

def safe_halt(reason: str):
    print(f"[SAFE_HALT] {reason}")
    sys.exit(1)

class PositionSizer:
    def __init__(self, system_config: dict):
        try:
            self._max_position_pct = system_config["safety_limits"]["max_position_pct"]
            
            if self._max_position_pct <= 0:
                safe_halt("PositionSizer Init Failure: max_position_pct must be positive")
        except KeyError as e:
            safe_halt(f"PositionSizer Init Failure: Missing safety_limits key {str(e)}")
        except Exception as e:
            safe_halt(f"PositionSizer Init Failure: {str(e)}")

    def calculate_size(self, account_balance: float, strategy_allocation_pct: float) -> float:
        try:
            if account_balance <= 0:
                safe_halt("Position Sizing Failure: account_balance must be positive")
                
            if strategy_allocation_pct <= 0:
                safe_halt("Position Sizing Failure: strategy_allocation_pct must be positive")

            if strategy_allocation_pct > self._max_position_pct:
                safe_halt("Safety Violation: allocation exceeds max_position_pct limit")

            position_size_amount = account_balance * strategy_allocation_pct
            
            return position_size_amount
            
        except Exception as e:
            safe_halt(f"Position Sizing Calculation Failure: {str(e)}")