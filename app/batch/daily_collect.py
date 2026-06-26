import argparse
from datetime import datetime
from app.collectors.krx.client import call_krx
from app.services.normalizer import krx_stock_daily_to_records
from app.services.repository import upsert_stock_prices

def run(bas_dd: str):
    df = call_krx("stock_daily", bas_dd)
    records = krx_stock_daily_to_records(df)
    count = upsert_stock_prices(records)
    print(f"[COLLECT] {bas_dd} stock_price_daily saved: {count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()
    run(args.date)
