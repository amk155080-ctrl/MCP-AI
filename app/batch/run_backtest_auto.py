from sqlalchemy import text
from app.core.database import SessionLocal

HOLD_DAYS = 5


def run():
    db = SessionLocal()
    saved = 0

    try:
        dates = db.execute(text("""
            SELECT DISTINCT trade_date
            FROM mcp4.recommendation_history
            ORDER BY trade_date
        """)).fetchall()

        dates = [r[0] for r in dates]

        for trade_date in dates:
            target = db.execute(text("""
                SELECT trade_date
                FROM mcp4.stock_price_daily
                WHERE trade_date > :trade_date
                GROUP BY trade_date
                ORDER BY trade_date
                OFFSET :offset
                LIMIT 1
            """), {
                "trade_date": trade_date,
                "offset": HOLD_DAYS - 1
            }).fetchone()

            if not target:
                print("[SKIP] no target date:", trade_date)
                continue

            sell_date = target[0]

            rows = db.execute(text("""
                SELECT
                    r.stock_code,
                    r.stock_name,
                    r.total_score,
                    r.confidence,
                    r.signal,
                    buy.close_price AS buy_price,
                    sell.close_price AS sell_price
                FROM mcp4.recommendation_history r
                JOIN mcp4.stock_price_daily buy
                  ON r.trade_date = buy.trade_date
                 AND r.stock_code = buy.stock_code
                JOIN mcp4.stock_price_daily sell
                  ON sell.trade_date = :sell_date
                 AND r.stock_code = sell.stock_code
                WHERE r.trade_date = :trade_date
            """), {
                "trade_date": trade_date,
                "sell_date": sell_date
            }).mappings().all()

            print("[BACKTEST]", trade_date, "->", sell_date, "rows:", len(rows))

            for row in rows:
                buy_price = float(row["buy_price"] or 0)
                sell_price = float(row["sell_price"] or 0)

                if buy_price <= 0:
                    continue

                ret = round((sell_price - buy_price) / buy_price * 100, 2)

                db.execute(text("""
                    INSERT INTO mcp4.backtest_result_daily
                    (
                        buy_date,
                        sell_date,
                        stock_code,
                        stock_name,
                        buy_price,
                        sell_price,
                        total_score,
                        confidence,
                        return_percent,
                        signal
                    )
                    VALUES
                    (
                        :buy_date,
                        :sell_date,
                        :stock_code,
                        :stock_name,
                        :buy_price,
                        :sell_price,
                        :total_score,
                        :confidence,
                        :return_percent,
                        :signal
                    )
                    ON CONFLICT (buy_date, sell_date, stock_code)
                    DO UPDATE SET
                        stock_name = EXCLUDED.stock_name,
                        buy_price = EXCLUDED.buy_price,
                        sell_price = EXCLUDED.sell_price,
                        total_score = EXCLUDED.total_score,
                        confidence = EXCLUDED.confidence,
                        return_percent = EXCLUDED.return_percent,
                        signal = EXCLUDED.signal
                """), {
                    "buy_date": trade_date,
                    "sell_date": sell_date,
                    "stock_code": row["stock_code"],
                    "stock_name": row["stock_name"],
                    "buy_price": buy_price,
                    "sell_price": sell_price,
                    "total_score": row["total_score"],
                    "confidence": row["confidence"],
                    "return_percent": ret,
                    "signal": row["signal"],
                })

                saved += 1

        db.commit()
        print("[AUTO BACKTEST COMPLETE] saved:", saved)

    finally:
        db.close()


if __name__ == "__main__":
    run()
