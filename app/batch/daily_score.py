import argparse
from datetime import datetime
from app.services.scoring import calculate_daily_scores

def run(bas_dd: str):
    trade_date = f"{bas_dd[:4]}-{bas_dd[4:6]}-{bas_dd[6:]}"
    count = calculate_daily_scores(trade_date)
    print(f"[SCORE] {trade_date} stock_score_daily saved: {count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()
    run(args.date)
