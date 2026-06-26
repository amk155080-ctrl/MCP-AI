import argparse
from datetime import datetime

from sqlalchemy import text

from app.core.database import SessionLocal


def run(bas_dd):
    trade_date = f"{bas_dd[0:4]}-{bas_dd[4:6]}-{bas_dd[6:8]}"

    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT DISTINCT
                    stock_code,
                    stock_name,
                    MAX(listed_shares) AS listed_shares
                FROM mcp4.stock_price_daily
                WHERE trade_date = :trade_date
                  AND stock_code IS NOT NULL
                  AND stock_name IS NOT NULL
                GROUP BY stock_code, stock_name
            """),
            {"trade_date": trade_date},
        ).mappings().all()

        saved = 0

        for r in rows:
            db.execute(
                text("""
                    INSERT INTO mcp4.stock_master
                    (
                        stock_code,
                        stock_name,
                        market_type,
                        sector_name,
                        listing_date,
                        listing_shares,
                        created_at,
                        updated_at
                    )
                    VALUES
                    (
                        :stock_code,
                        :stock_name,
                        :market_type,
                        :sector_name,
                        NULL,
                        :listing_shares,
                        NOW(),
                        NOW()
                    )
                    ON CONFLICT (stock_code)
                    DO UPDATE SET
                        stock_name = EXCLUDED.stock_name,
                        market_type = EXCLUDED.market_type,
                        listing_shares = EXCLUDED.listing_shares,
                        updated_at = NOW()
                """),
                {
                    "stock_code": r["stock_code"],
                    "stock_name": r["stock_name"],
                    "market_type": "KOSPI_KOSDAQ",
                    "sector_name": None,
                    "listing_shares": r["listed_shares"],
                },
            )
            saved += 1

        db.commit()

    finally:
        db.close()

    print("[STOCK MASTER]", trade_date, "saved:", saved)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    run(args.date)
