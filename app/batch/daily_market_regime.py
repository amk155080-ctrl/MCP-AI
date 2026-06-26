import argparse
from datetime import datetime

from sqlalchemy import text

from app.core.database import SessionLocal
from app.collectors.macro.yfinance_client import fetch_macro_snapshot
from app.engines.market_regime import calculate_market_regime


def run(bas_dd):
    trade_date = f"{bas_dd[0:4]}-{bas_dd[4:6]}-{bas_dd[6:8]}"

    snapshot, returns = fetch_macro_snapshot()

    snapshot["trade_date"] = trade_date

    result = calculate_market_regime(
        returns.get("sox_return", 0),
        snapshot.get("vix"),
        snapshot.get("us10y"),
        snapshot.get("dxy"),
    )

    db = SessionLocal()

    try:
        db.execute(
            text(
                """
                INSERT INTO mcp4.market_regime_daily
                (
                    trade_date,
                    sox_score,
                    vix_score,
                    us10y_score,
                    dxy_score,
                    liquidity_score,
                    total_score,
                    regime
                )
                VALUES
                (
                    :trade_date,
                    :sox_score,
                    :vix_score,
                    :us10y_score,
                    :dxy_score,
                    :liquidity_score,
                    :total_score,
                    :regime
                )
                ON CONFLICT (trade_date)
                DO UPDATE SET
                    sox_score = EXCLUDED.sox_score,
                    vix_score = EXCLUDED.vix_score,
                    us10y_score = EXCLUDED.us10y_score,
                    dxy_score = EXCLUDED.dxy_score,
                    liquidity_score = EXCLUDED.liquidity_score,
                    total_score = EXCLUDED.total_score,
                    regime = EXCLUDED.regime
                """
            ),
            {
                "trade_date": trade_date,
                "sox_score": result.sox_score,
                "vix_score": result.vix_score,
                "us10y_score": result.us10y_score,
                "dxy_score": result.dxy_score,
                "liquidity_score": result.liquidity_score,
                "total_score": result.score,
                "regime": result.regime,
            },
        )

        db.commit()

    finally:
        db.close()

    print("[MARKET]", trade_date, result.regime, result.score)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    run(args.date)
