import hashlib
import json
import sys

def safe_halt(reason: str):
    print(f"[SAFE_HALT] {reason}")
    sys.exit(1)

class OrderIntent:
    def __init__(self, system_config: dict, symbol: str, side: str, quantity: float, timestamp: int):
        try:
            # SSOT: system_config.yaml -> safety_limits -> max_holding_minutes 참조
            # unit conversion: minutes to seconds (60s/1m)
            self._max_holding_min = system_config["safety_limits"]["max_holding_minutes"]
            
            if self._max_holding_min <= 0:
                safe_halt("OrderIntent Init Failure: max_holding_minutes must be positive")

            self.symbol = symbol
            self.side = side
            self.quantity = quantity
            self.timestamp = timestamp
            self.ttl_seconds = self._max_holding_min * 60
            
            self.intent_id = self._generate_idempotency_key()
            
            if not self.intent_id:
                safe_halt("OrderIntent Init Failure: intent_id generation returned null")
                
        except KeyError as e:
            safe_halt(f"OrderIntent Init Failure: Missing SSOT key {str(e)}")
        except Exception as e:
            safe_halt(f"OrderIntent Initialization Failure: {str(e)}")

    def _generate_idempotency_key(self) -> str:
        try:
            # Deterministic payload for hash consistency
            intent_data = {
                "symbol": self.symbol,
                "side": self.side,
                "quantity": self.quantity,
                "timestamp": self.timestamp
            }
            payload = json.dumps(intent_data, sort_keys=True)
            generated_hash = hashlib.sha256(payload.encode()).hexdigest()
            
            if not generated_hash:
                safe_halt("Idempotency Key Generation Failure: Hash is empty")
                
            return generated_hash
            
        except Exception as e:
            safe_halt(f"Idempotency Key Generation Failure: {str(e)}")

    def to_dict(self) -> dict:
        try:
            return {
                "intent_id": self.intent_id,
                "symbol": self.symbol,
                "side": self.side,
                "quantity": self.quantity,
                "timestamp": self.timestamp,
                "ttl_seconds": self.ttl_seconds
            }
        except Exception as e:
            safe_halt(f"OrderIntent Export Failure: {str(e)}")