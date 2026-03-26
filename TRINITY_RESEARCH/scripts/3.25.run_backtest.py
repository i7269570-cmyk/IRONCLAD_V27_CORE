import sys
import os
import glob
import pandas as pd

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.strategies.orb.strategy import ORBStrategy
from src.core.backtest_engine import BacktestEngine
from src.strategies.momentum.strategy import MomentumStrategy
from src.strategies.pullback.strategy import PullbackStrategy

# -------------------------
# 데이터 로드
# -------------------------
def load_data(data_path):
    df_list = []
    symbols = os.listdir(data_path)

    print(f"🔍 LS증권 주식 필터링 시작 (대상: {len(symbols)}개 종목)...")

    for symbol in symbols:
        symbol_path = os.path.join(data_path, symbol)
        if not os.path.isdir(symbol_path):
            continue

        files = glob.glob(os.path.join(symbol_path, "*.csv"))

        for file in files:
            df = pd.read_csv(file)
            df["symbol"] = symbol
            df_list.append(df)

    if not df_list:
        raise ValueError("❌ 데이터 없음")

    data = pd.concat(df_list)
    data = data.sort_values(["symbol", "date", "time"])

    print(f"✅ 필터링 완료: {len(data['symbol'].unique())}개 주식 선정")
    return data


# -------------------------
# 전략 실행 함수
# -------------------------
def run_strategy(strategy_class, data, name):
    print(f"\n===== 🚀 Running LS Securities Strategy: {name} =====")

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

    print(f"📝 결과 저장 완료: {output_path}")


# -------------------------
# 메인 실행
# -------------------------
if __name__ == "__main__":

    DATA_PATH = "data/processed/stock"

    try:
        data = load_data(DATA_PATH)

        # Pullback 실행
        run_strategy(
            PullbackStrategy,
            data,
            "ls_pullback_v1"
        )
        
        # ORB 실행
        run_strategy(
            ORBStrategy,
            data,
            "ls_orb_v1"
        )

    except Exception as e:
        print(f"⚠️ 실행 오류 발생: {e}")