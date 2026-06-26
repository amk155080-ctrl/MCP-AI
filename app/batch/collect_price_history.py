import argparse
import subprocess
import sys
from datetime import datetime, timedelta


def ymd(d):
    return d.strftime("%Y%m%d")


def run(start, end):
    start_date = datetime.strptime(start, "%Y%m%d").date()
    end_date = datetime.strptime(end, "%Y%m%d").date()

    d = start_date

    while d <= end_date:
        # 주말 제외
        if d.weekday() < 5:
            date_str = ymd(d)

            print("=" * 70)
            print("[PRICE HISTORY]", date_str)
            print("=" * 70)

            cmd = [
                sys.executable,
                "-m",
                "app.batch.collect_krx_stock_price_all",
                "--date",
                date_str,
            ]

            result = subprocess.run(cmd)

            if result.returncode != 0:
                print("[WARN] failed:", date_str)

        d += timedelta(days=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    args = parser.parse_args()

    run(args.start, args.end)
