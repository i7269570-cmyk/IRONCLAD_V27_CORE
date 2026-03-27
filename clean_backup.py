import pandas as pd
import numpy as np
import os

TRADES_DIR  = "results/trades"
BARS_PER_DAY = 390          # 1?? ?? (09:00~15:30), ??? ??


def analyze(df: pd.DataFrame, strategy_name: str) -> dict:
    if df.empty:
        return {"strategy": strategy_name, "error": "no trades"}

    wins   = df[df["result"] == "WIN"]
    losses = df[df["result"] == "LOSS"]

    total        = len(df)
    win_rate     = len(wins) / total if total else 0
    avg_win      = wins["pnl_net"].mean()   if len(wins)   else 0
    avg_loss     = losses["pnl_net"].mean() if len(losses) else 0
    profit_factor = (
        (wins["pnl_net"].sum() / abs(losses["pnl_net"].sum()))
        if len(losses) > 0 and losses["pnl_net"].sum() != 0
        else np.inf
    )
    max_loss     = df["pnl_net"].min()
    avg_hold     = df["hold_bars"].mean()
    avg_pnl_net  = df["pnl_net"].mean()
    total_pnl    = df["pnl_net"].sum()

    # ? ?? ?? ? ?? (? ? ?? ??)
    bar_range    = df["exit_idx"].max() - df["entry_idx"].min() + 1 if total > 1 else 1
    est_days     = max(bar_range / BARS_PER_DAY, 1)
    trades_per_day = total / est_days

    return {
        "strategy"       : strategy_name,
        "total_trades"   : total,
        "win_rate"       : round(win_rate, 4),
        "avg_pnl_net"    : round(avg_pnl_net,  6),
        "avg_win"        : round(avg_win,       6),
        "avg_loss"       : round(avg_loss,      6),
        "profit_factor"  : round(profit_factor, 4),
        "max_loss"       : round(max_loss,      6),
        "avg_hold_bars"  : round(avg_hold,      1),
        "est_trades_day" : round(trades_per_day, 2),
        "total_pnl_net"  : round(total_pnl,     6),
    }


def print_summary(stats: dict):
    print("=" * 52)
    print(f"  ?? : {stats['strategy']}")
    print("=" * 52)
    if "error" in stats:
        print(f"  [WARN] {stats['error']}")
        return
    rows = [
        ("? ?? ?",        stats["total_trades"]),
        ("??",             f"{stats['win_rate']:.1%}"),
        ("?? ??? (net)", f"{stats['avg_pnl_net']:.4%}"),
        ("?? ?? ??",    f"{stats['avg_win']:.4%}"),
        ("?? ?? ??",    f"{stats['avg_loss']:.4%}"),
        ("Profit Factor",    stats["profit_factor"]),
        ("?? ?? ??",   f"{stats['max_loss']:.4%}"),
        ("?? ?? ?",     stats["avg_hold_bars"]),
        ("? ?? ?? ?",  stats["est_trades_day"]),
        ("?? ????",    f"{stats['total_pnl_net']:.4%}"),
    ]
    for label, val in rows:
        print(f"  {label:<20} {val}")
    print()


def main():
    strategy_names = [
        "MomentumVolumeBreakout",
        "MeanReversionBB",
    ]

    all_stats = []

    for name in strategy_names:
        fpath = os.path.join(TRADES_DIR, f"trades_{name}.csv")
        if not os.path.exists(fpath):
            print(f"[SKIP] {fpath} ??")
            continue

        df    = pd.read_csv(fpath)
        stats = analyze(df, name)
        print_summary(stats)
        all_stats.append(stats)

    # ?? ??? ??
    if all_stats:
        summary_df = pd.DataFrame(all_stats)
        out_path   = os.path.join(TRADES_DIR, "strategy_comparison.csv")
        summary_df.to_csv(out_path, index=False)
        print(f"[SAVED] {out_path}")


if __name__ == "__main__":
    main()