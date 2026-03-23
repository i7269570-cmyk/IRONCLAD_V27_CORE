import os
import yaml
import json
import datetime

BASE_DIR = os.path.dirname(__file__)
STATE_PATH = os.path.join(BASE_DIR, "state.json")


# STATE
def load_state():
    if not os.path.exists(STATE_PATH):
        return {"position": "FLAT", "entry_price": None, "last_update": None}
    with open(STATE_PATH, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


# STRATEGY
def load_strategy():
    path = os.path.join(BASE_DIR, "strategy_spec.yaml")
    if not os.path.exists(path):
        raise FileNotFoundError("strategy_spec.yaml 없음")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# SCHEDULER
def scheduler():
    h = datetime.datetime.now().hour
    if h < 11:
        return "morning"
    elif h < 14:
        return "sideways"
    else:
        return "afternoon"


# ENTRY
def entry_engine(strategy_name, strategy_spec):
    strategy = strategy_spec["strategies"].get(strategy_name)
    if not strategy:
        return False

    cond = strategy.get("condition", {})

    # 테스트용 더미
    gap = 3
    vol = 800000
    rng = 1.2
    atr = 1.0

    if strategy_name == "morning":
        if gap >= cond.get("gap_pct", 999) and vol >= cond.get("volume_multiplier", 999):
            print("진입: morning")
            return True

    elif strategy_name == "sideways":
        if rng <= cond.get("range_pct", 999) and atr <= cond.get("atr_multiplier", 999) and vol >= cond.get("min_volume", 0):
            print("진입: sideways")
            return True

    elif strategy_name == "afternoon":
        if gap >= cond.get("gap_pct", 999) or vol >= cond.get("volume_multiplier", 999):
            print("진입: afternoon")
            return True

    return False


# EXIT (간단 테스트용)
def exit_engine(state):
    if state["position"] != "LONG":
        return False
    # 예: 5% 이상 오르면 청산 (더미)
    current_price = 102  # 나중에 실제 가격
    if current_price >= state["entry_price"] * 1.05:
        print("청산: +5%")
        return True
    return False


# MAIN
def main():
    state = load_state()
    spec = load_strategy()
    name = scheduler()

    print(f"전략: {name}")

    if state["position"] == "FLAT":
        if entry_engine(name, spec):
            print("BUY")
            state["position"] = "LONG"
            state["entry_price"] = 100  # 나중에 실제 가격

    elif state["position"] == "LONG":
        if exit_engine(state):
            print("SELL")
            state["position"] = "FLAT"

    state["last_update"] = datetime.datetime.now().isoformat()
    save_state(state)


if __name__ == "__main__":
    main()