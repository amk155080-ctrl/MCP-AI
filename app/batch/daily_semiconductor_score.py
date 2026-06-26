import argparse
from datetime import datetime
from sqlalchemy import text
from app.core.database import SessionLocal
from app.engines.semiconductor import calculate_semiconductor_score

def run(trade_date):
    db = SessionLocal()
    try:
        m = db.execute(text('SELECT total_score FROM mcp4.market_regime_daily ORDER BY trade_date DESC LIMIT 1')).fetchone()
        market_score = float(m.total_score) if m else 50
        stocks = db.execute(text('SELECT * FROM mcp4.semiconductor_universe ORDER BY weight_score DESC')).fetchall()
        for row in stocks:
            r = calculate_semiconductor_score(row, market_score)
            r["trade_date"] = trade_date
            db.execute(text('''
                INSERT INTO mcp4.semiconductor_score_daily
                (trade_date, stock_code, stock_name, sox_score, nvda_score, hbm_score, flow_score, earnings_score, total_score, grade)
                VALUES (:trade_date, :stock_code, :stock_name, :sox_score, :nvda_score, :hbm_score, :flow_score, :earnings_score, :total_score, :grade)
                ON CONFLICT (trade_date, stock_code) DO UPDATE SET
                stock_name=EXCLUDED.stock_name, sox_score=EXCLUDED.sox_score, nvda_score=EXCLUDED.nvda_score,
                hbm_score=EXCLUDED.hbm_score, flow_score=EXCLUDED.flow_score, earnings_score=EXCLUDED.earnings_score,
                total_score=EXCLUDED.total_score, grade=EXCLUDED.grade
            '''), r)
        db.commit()
    finally:
        db.close()
    print("[SEMICONDUCTOR]", trade_date, "saved")

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    run(p.parse_args().date)
