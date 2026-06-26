import argparse
import subprocess
import sys
from datetime import datetime


JOBS = [
    ("KRX Price All", "app.batch.collect_krx_stock_price_all"),
    ("Stock Master Build", "app.batch.build_stock_master_from_price"),
    ("Investor Flow All", "app.batch.collect_krx_investor_flow"),
    ("Market Regime", "app.batch.daily_market_regime"),
    ("Stock Score All V4", "app.batch.daily_stock_score_all"),
    ("Short / Loan", "app.batch.collect_krx_short_loan"),
    ("Institutional Score V5", "app.batch.daily_institutional_score"),
    ("Portfolio Build", "app.batch.daily_portfolio_build"),
    ("Risk Build", "app.batch.daily_risk_build"),
    ("Backtest Run", "app.batch.daily_backtest_run"),
]


def run_job(name, module, date):
    print("=" * 80)
    print(f"[RUN] {name} | {date}")
    print("=" * 80)

    cmd = [
        sys.executable,
        "-m",
        module,
        "--date",
        date,
    ]

    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"[FAILED] {name}")
        raise SystemExit(result.returncode)

    print(f"[OK] {name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    print("=" * 80)
    print(f"[MCP4 DAILY V4 PIPELINE START] {args.date}")
    print("=" * 80)

    for name, module in JOBS:
        run_job(name, module, args.date)

    print("=" * 80)
    print(f"[MCP4 DAILY V4 PIPELINE DONE] {args.date}")
    print("=" * 80)

    print("")
    print("[NEXT API CHECK]")
    print("curl 'http://127.0.0.1:8000/api/v4/ranking/institutional_quality_buy?limit=10'")
    print("curl 'http://127.0.0.1:8000/api/v4/ranking/institutional_quality_sell?limit=10'")
    print("curl 'http://127.0.0.1:8000/api/v4/portfolio/compare?capital=10000000&limit=5'")


if __name__ == "__main__":
    main()
