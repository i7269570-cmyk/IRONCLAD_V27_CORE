import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.strategies.momentum_volume.strategy import MomentumVolumeBreakoutStrategy
from src.strategies.mean_reversion.strategy import MeanReversionBBStrategy
from src.core.backtest_engine import BacktestEngine


def load_data(data_path):

    df_list = []

    files = os.listdir(data_path)
    print("로드된 파일 수:", len(files))

    for file in files:

        if not file.endswith(".csv"):
            continue

        path = os.path.join(data_path, file)

        try:
            df = pd.read_csv(path)

            symbol = file.replace(".csv", "")
            df["symbol"] = symbol

            df_list.append(df)

        except Exception as e:
            print("에러:", file, e)

    data = pd.concat(df_list, ignore_index=True)

    return data


def run_strategy(strategy_class, data, name):
    print(f"\n===== 🚀 {name} 실행 중 =====")

    strategy = strategy_class()

    engine = BacktestEngine(
        strategy=strategy,
        initial_cash=10_000_000,
    )

    results = engine.run(data)

    print(f"✅ {name} 완료 | 거래수: {len(results['trades'])}")

    return results


if __name__ == "__main__":

    DATA_PATH = "data/processed"

    data = load_data(DATA_PATH)

    # 🔥 기간 분리
    train = data[data["date"] < 20250101]
    test  = data[data["date"] >= 20250101]

    print("훈련 데이터:", len(train))
    print("검증 데이터:", len(test))

    # 🔥 핵심 수정: test 기준으로 종목 추출
    symbols = test["symbol"].unique()

    print("검증 종목 수:", len(symbols))

    all_trades_mv = []
    all_trades_mr = []

    for symbol in symbols:

        symbol_data = test[test["symbol"] == symbol]

        if len(symbol_data) < 50:
            continue

        print(f"\n📊 종목 실행: {symbol} | 데이터: {len(symbol_data)}")

        mv_result = run_strategy(
            MomentumVolumeBreakoutStrategy,
            symbol_data,
            f"ls_momentum_volume_{symbol}"
        )

        mr_result = run_strategy(
            MeanReversionBBStrategy,
            symbol_data,
            f"ls_mean_reversion_{symbol}"
        )

        if mv_result["trades"] is not None:
            all_trades_mv.append(mv_result["trades"])

        if mr_result["trades"] is not None:
            all_trades_mr.append(mr_result["trades"])

    # =========================
    # 🔥 전체 통합 결과 계산
    # =========================

    def analyze(trades_df, name):

        if len(trades_df) == 0:
            print(f"\n===== {name} =====")
            print("거래 없음")
            return

        pnl = trades_df["pnl"]

        total = len(pnl)
        win_rate = (pnl > 0).mean()
        profit_factor = pnl[pnl > 0].sum() / abs(pnl[pnl < 0].sum())

        print(f"\n===== {name} =====")
        print("총 거래수:", total)
        print("승률:", round(win_rate, 3))
        print("PF:", round(profit_factor, 3))
        print("평균 수익:", round(pnl.mean(), 6))


    if len(all_trades_mv) > 0:
        analyze(pd.concat(all_trades_mv), "LS_MOMENTUM_VOLUME (TEST)")

    if len(all_trades_mr) > 0:
        analyze(pd.concat(all_trades_mr), "LS_MEAN_REVERSION (TEST)")