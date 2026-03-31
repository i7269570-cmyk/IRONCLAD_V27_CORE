import os
import math
import pandas as pd
import yfinance as yf
import ccxt

SAVE_PATH = os.path.join(os.path.dirname(__file__), "../data/target_100.csv")


def to_scalar(x):
    """
    pandas Series / numpy scalar / 일반 값을 모두 안전하게 float로 변환
    """
    try:
        if hasattr(x, "iloc"):
            x = x.iloc[-1]
        if hasattr(x, "item"):
            try:
                x = x.item()
            except Exception:
                pass
        return float(x)
    except Exception:
        return math.nan


# =========================
# 1. 주식
# =========================
def get_stock_universe():
    tickers = [
        "005930.KS", "000660.KS", "035420.KS",
        "AAPL", "MSFT", "NVDA", "TSLA"
    ]

    rows = []

    for ticker in tickers:
        try:
            df = yf.download(
                ticker,
                period="5d",
                interval="1d",
                auto_adjust=False,
                progress=False
            ).dropna()

            if len(df) < 2:
                continue

            close = to_scalar(df["Close"].iloc[-1])
            prev_close = to_scalar(df["Close"].iloc[-2])
            volume = to_scalar(df["Volume"].iloc[-1])

            if pd.isna(close) or pd.isna(prev_close) or pd.isna(volume):
                continue
            if close <= 0 or prev_close <= 0 or volume <= 0:
                continue

            value = close * volume
            change_rate = ((close - prev_close) / prev_close) * 100.0

            rows.append({
                "symbol": str(ticker),
                "price": float(close),
                "value": float(value),
                "change_rate": float(change_rate),
                "asset_type": "STOCK"
            })

        except Exception:
            continue

    stock_df = pd.DataFrame(rows, columns=["symbol", "price", "value", "change_rate", "asset_type"])

    if stock_df.empty:
        raise ValueError("STOCK_UNIVERSE_EMPTY")

    stock_df["price"] = pd.to_numeric(stock_df["price"], errors="coerce")
    stock_df["value"] = pd.to_numeric(stock_df["value"], errors="coerce")
    stock_df["change_rate"] = pd.to_numeric(stock_df["change_rate"], errors="coerce")
    stock_df = stock_df.dropna(subset=["symbol", "price", "value", "change_rate"])

    if stock_df.empty:
        raise ValueError("STOCK_UNIVERSE_EMPTY_AFTER_CLEAN")

    return stock_df.sort_values(
        by=["value", "change_rate"],
        ascending=[False, False]
    ).head(100)


# =========================
# 2. 코인
# =========================
def get_crypto_universe():
    exchange = ccxt.binance()
    markets = exchange.load_markets()

    symbols = [s for s in markets if "/USDT" in s][:200]
    rows = []

    for symbol in symbols:
        try:
            ticker = exchange.fetch_ticker(symbol)

            last = ticker.get("last")
            quote_volume = ticker.get("quoteVolume")
            high = ticker.get("high")
            low = ticker.get("low")

            price = to_scalar(last)
            value = to_scalar(quote_volume)
            high = to_scalar(high)
            low = to_scalar(low)

            if pd.isna(price) or pd.isna(value) or pd.isna(high) or pd.isna(low):
                continue
            if price <= 0 or value <= 0 or low <= 0:
                continue

            change_rate = ((high - low) / low) * 100.0

            rows.append({
                "symbol": str(symbol),
                "price": float(price),
                "value": float(value),
                "change_rate": float(change_rate),
                "asset_type": "CRYPTO"
            })

        except Exception:
            continue

    crypto_df = pd.DataFrame(rows, columns=["symbol", "price", "value", "change_rate", "asset_type"])

    if crypto_df.empty:
        raise ValueError("CRYPTO_UNIVERSE_EMPTY")

    crypto_df["price"] = pd.to_numeric(crypto_df["price"], errors="coerce")
    crypto_df["value"] = pd.to_numeric(crypto_df["value"], errors="coerce")
    crypto_df["change_rate"] = pd.to_numeric(crypto_df["change_rate"], errors="coerce")
    crypto_df = crypto_df.dropna(subset=["symbol", "price", "value", "change_rate"])

    if crypto_df.empty:
        raise ValueError("CRYPTO_UNIVERSE_EMPTY_AFTER_CLEAN")

    return crypto_df.sort_values(
        by=["value", "change_rate"],
        ascending=[False, False]
    ).head(100)


# =========================
# 3. 병합
# =========================
def build_universe():
    stock_df = get_stock_universe()
    crypto_df = get_crypto_universe()

    combined = pd.concat([stock_df, crypto_df], ignore_index=True)
    combined.to_csv(SAVE_PATH, index=False, encoding="utf-8-sig")

    print("UNIVERSE GENERATED:", len(combined))
    print(combined.head(5))


if __name__ == "__main__":
    build_universe()