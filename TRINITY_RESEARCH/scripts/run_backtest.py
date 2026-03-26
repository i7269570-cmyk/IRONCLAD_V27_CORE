import sys
import os
import glob
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.strategies.momentum_volume.strategy import MomentumVolumeBreakoutStrategy
from src.strategies.mean_reversion.strategy import MeanReversionBBStrategy
from src.core.backtest_engine import BacktestEngine

def load_data(data_path):
    df_list = []
    symbols = os.listdir(data_path)

    print(f"🔍 데이터 로드 시작...")

    for symbol in symbols:
        symbol_path = os.path.join(data_path, symbol)
        if not os.path.isdir(symbol_path):
            continue

        for file in glob.glob(os.path.join(symbol_path, "*.csv")):
            df = pd.read_csv(file)
            df["symbol"] = symbol
            df_list.append(df)

    data = pd.concat(df_list)
    data = data.sort_values(["symbol", "date", "time"])
    print(f"✅ 총 {len(data['symbol'].unique())}개 종목 로드 완료")
    return data


def run_strategy(strategy_class, data, name):
    print(f"\n===== 🚀 {name} 실행 중 =====")

    strategy = strategy_class()

    engine = BacktestEngine(
        strategy=strategy,
        initial_cash=10_000_000,
    )

    results = engine.run(data)

    output_path = f"output/{name}"
    os.makedirs(output_path, exist_ok=True)

    results["trades"].to_csv(f"{output_path}/trades.csv", index=False)
    results["equity_curve"].to_csv(f"{output_path}/equity.csv", index=False)

    print(f"✅ {name} 완료 | 거래수: {len(results['trades'])}")


if __name__ == "__main__":
    DATA_PATH = "data/processed/stock"

    data = load_data(DATA_PATH)

    # 두 전략 실행
    run_strategy(MomentumVolumeBreakoutStrategy, data, "ls_momentum_volume")
    run_strategy(MeanReversionBBStrategy, data, "ls_mean_reversion")