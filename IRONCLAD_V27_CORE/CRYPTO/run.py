import os
import yaml
import json
import datetime

BASE_DIR = os.path.dirname(__file__)
STATE_PATH = os.path.join(BASE_DIR, "state.json")


# ---------------------------
# STATE
# ---------------------------
def load_state():
    if not os.path.exists(STATE_PATH):
        return {
            "position": "FLAT",
            "entry_price": None,
            "last_update": None
        }
    with open(STATE_PATH, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


# ---------------------------
# STRATEGY
# ---------------------------
def load_strategy():
    path = os.path.join(BASE_DIR, "strategy_spec.yaml")
    if not os.path.exists(path):
        raise FileNotFoundError("strategy_spec.yaml 없음")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------
# SCHEDULER (시간 기반 전략 선택)
# ---------------------------
def scheduler():
    now = datetime.datetime.now().time()

    if now.hour < 11:
        return "morning"
    elif now.hour < 14:
        return "sideways"
    else:
        return "afternoon"


# ---------------------------
# ENTRY (아직 조건 없음 → 안전 상태)
# ---------------------------
def entry_engine(strategy_name, strategy_spec):
    strategy = strategy_spec["strategies"].get(strategy_name)

    if not strategy:
        return False

    # 현재는 조건 미구현 → 항상 False
    return False


# ---------------------------
# EXIT (아직 조건 없음)
# ---------------------------
def exit_engine(state):
    return False


# ---------------------------
# MAIN
# ---------------------------
def main():
    state = load_state()
    strategy_spec = load_strategy()

    # 현재 시간 기준 전략 선택
    strategy_name = scheduler()

    print(f"현재 전략: {strategy_name}")

    if state["position"] == "FLAT":
        if entry_engine(strategy_name, strategy_spec):
            print("BUY")
            state["position"] = "LONG"
            state["entry_price"] = 100  # 나중에 API 연결

    elif state["position"] == "LONG":
        if exit_engine(state):
            print("SELL")
            state["position"] = "FLAT"

    state["last_update"] = datetime.datetime.now().isoformat()
    save_state(state)


if __name__ == "__main__":
    main()