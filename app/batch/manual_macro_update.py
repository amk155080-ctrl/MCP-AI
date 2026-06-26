import argparse
from datetime import datetime

from sqlalchemy import text

from app.core.database import SessionLocal
from app.engines.market_regime import calculate_market_regime


def run(trade_date, sox, sox_return, vix, us10y, dxy):
    result = calculate_market_regime(
        sox_return=sox_return,
        vix=vix,
        us10y=us10y,
        dxy=dxy,
        deposit_change=0,
        margin_change=0,
    )

    db = SessionLocal()

    try:
        db.execute(
            text(
                """
                INSERT INTO mcp4.macro_daily
                (trade_date, sox, vix, us10y, dxy)
                VALUES (:trade_date, :sox, :vix, :us10y, :dxy)
                ON CONFLICT (trade_date)
                DO UPDATE SET
                    sox = EXCLUDED.sox,
                    vix = EXCLUDED.vix,
                    us10y = EXCLUDED.us10y,
                    dxy = EXCLUDED.dxy
                """
            ),
            {
                "trade_date": trade_date,
                "sox": sox,
                "vix": vix,
                "us10y": us10y,
                "dxy": dxy,
            },
        )

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

    print("[MANUAL MACRO]", trade_date, result.regime, result.score)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--sox", type=float, required=True)
    parser.add_argument("--sox-return", type=float, required=True)
    parser.add_argument("--vix", type=float, required=True)
    parser.add_argument("--us10y", type=float, required=True)
    parser.add_argument("--dxy", type=float, required=True)

    args = parser.parse_args()

    run(
        trade_date=args.date,
        sox=args.sox,
        sox_return=args.sox_return,
        vix=args.vix,
        us10y=args.us10y,
        dxy=args.dxy,
    )
