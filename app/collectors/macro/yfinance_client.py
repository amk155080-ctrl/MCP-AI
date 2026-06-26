import pandas as pd
import yfinance as yf


TICKERS = {
    "sox": "^SOX",
    "nasdaq": "^IXIC",
    "sp500": "^GSPC",
    "vix": "^VIX",
    "us10y": "^TNX",
    "dxy": "DX-Y.NYB",
}


DEFAULT_SNAPSHOT = {
    "sox": 0.0,
    "nasdaq": 0.0,
    "sp500": 0.0,
    "vix": 20.0,
    "us10y": 45.0,
    "dxy": 105.0,
}


DEFAULT_RETURNS = {
    "sox_return": 0.0,
    "nasdaq_return": 0.0,
    "sp500_return": 0.0,
    "vix_return": 0.0,
    "us10y_return": 0.0,
    "dxy_return": 0.0,
}


def _latest_close(ticker):
    try:
        df = yf.download(
            ticker,
            period="7d",
            interval="1d",
            progress=False,
            auto_adjust=False,
        ).dropna()

        if df.empty:
            return None, None, None

        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) >= 2 else df.iloc[-1]

        d = pd.to_datetime(df.index[-1]).date()

        close = float(last["Close"])
        prev_close = float(prev["Close"])

        ret = ((close - prev_close) / prev_close * 100) if prev_close else 0.0

        return d, close, ret

    except Exception as e:
        print("[WARN] yfinance failed:", ticker, e)
        return None, None, None


def fetch_macro_snapshot():
    result = {"trade_date": None}
    returns = {}

    for key, ticker in TICKERS.items():
        d, close, ret = _latest_close(ticker)

        if d is None:
            result[key] = DEFAULT_SNAPSHOT[key]
            returns[f"{key}_return"] = DEFAULT_RETURNS[f"{key}_return"]
            continue

        result["trade_date"] = d if result["trade_date"] is None else max(result["trade_date"], d)
        result[key] = close
        returns[f"{key}_return"] = ret

    return result, returns
