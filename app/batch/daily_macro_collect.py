from sqlalchemy import text
from app.core.database import SessionLocal
from app.collectors.macro.yfinance_client import fetch_macro_snapshot

def run():
    snapshot, _ = fetch_macro_snapshot()
    if not snapshot.get("trade_date"):
        raise RuntimeError("macro data fetch failed")
    db = SessionLocal()
    try:
        db.execute(text('''
            INSERT INTO mcp4.macro_daily (trade_date, sox, nasdaq, sp500, vix, us10y, dxy)
            VALUES (:trade_date, :sox, :nasdaq, :sp500, :vix, :us10y, :dxy)
            ON CONFLICT (trade_date) DO UPDATE SET
            sox=EXCLUDED.sox, nasdaq=EXCLUDED.nasdaq, sp500=EXCLUDED.sp500,
            vix=EXCLUDED.vix, us10y=EXCLUDED.us10y, dxy=EXCLUDED.dxy
        '''), snapshot)
        db.commit()
    finally:
        db.close()
    print("[MACRO]", snapshot["trade_date"], snapshot)

if __name__ == "__main__":
    run()
