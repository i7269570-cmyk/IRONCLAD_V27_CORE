def process_exits(mode, current_state, strategy_path):

    positions = list(current_state.get("positions", {}).values())

    exit_signals = []

    # ✅ FORCE_EXIT는 무조건 전량 청산
    if mode == "FORCE_EXIT":
        for pos in positions:
            exit_signals.append({
                **pos,
                "side": "SELL",
                "reason": "FORCE_EXIT",
                "asset_type": pos.get("asset_type")
            })
        return exit_signals

    # === 기존 로직 유지 ===
    import yaml, os

    with open(os.path.join(strategy_path, "exit_rules.yaml"), "r") as f:
        rules = yaml.safe_load(f)["conditions"]

    for pos in positions:

        pos["hold_bars"] = pos.get("hold_bars", 0) + 1

        entry_price = pos["entry_price"]
        current_price = pos.get("current_price", entry_price)
        profit = (current_price - entry_price) / entry_price

        for cond in rules:
            field = cond["field"]
            op = cond["op"]
            value = cond["value"]

            left = profit if field == "profit" else pos.get(field)

            if isinstance(value, str):
                value = eval(value, {}, pos)

            if (op == ">=" and left >= value) or (op == "<=" and left <= value):
                exit_signals.append({
                    **pos,
                    "side": "SELL",
                    "reason": "RULE_EXIT",
                    "asset_type": pos.get("asset_type")
                })
                break

    return exit_signals