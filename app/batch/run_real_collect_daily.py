import argparse
import subprocess
import sys
from datetime import datetime


def run_cmd(cmd, allow_fail=False):
    print("\n==============================")
    print("[RUN]", " ".join(cmd))
    print("==============================")

    result = subprocess.run(cmd)

    if result.returncode != 0:
        print("[WARN]", "failed:", " ".join(cmd))

        if not allow_fail:
            sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--capital", default="10000000")
    args = parser.parse_args()

    ymd = args.date
    dash_date = f"{ymd[0:4]}-{ymd[4:6]}-{ymd[6:8]}"

    print("\n[MCP 4.0 REAL DAILY COLLECT START]", dash_date)

    # 1. KRX 주가
    run_cmd([
        sys.executable,
        "-m",
        "app.batch.daily_collect",
        "--date",
        ymd,
    ])

    # 2. KRX 투자자 수급
    run_cmd([
        sys.executable,
        "-m",
        "app.batch.collect_krx_investor_flow",
        "--date",
        ymd,
    ], allow_fail=True)

    # 3. KRX 공매도 / 대차잔고
    run_cmd([
        sys.executable,
        "-m",
        "app.batch.collect_krx_short_loan",
        "--date",
        ymd,
    ], allow_fail=True)

    # 4. ECOS 매크로
    run_cmd([
        sys.executable,
        "-m",
        "app.batch.collect_ecos_macro",
        "--date",
        ymd,
    ], allow_fail=True)

    # 5. DART 실적
    run_cmd([
        sys.executable,
        "-m",
        "app.batch.collect_dart_earnings",
        "--date",
        ymd,
    ], allow_fail=True)

    # 6. 점수 계산
    run_cmd([
        sys.executable,
        "-m",
        "app.batch.daily_semiconductor_score",
        "--date",
        dash_date,
    ])

    run_cmd([
        sys.executable,
        "-m",
        "app.batch.daily_institutional_score",
        "--date",
        dash_date,
    ])

    run_cmd([
        sys.executable,
        "-m",
        "app.batch.daily_portfolio_build",
        "--date",
        dash_date,
    ])

    run_cmd([
        sys.executable,
        "-m",
        "app.batch.daily_risk_build",
        "--date",
        dash_date,
        "--portfolio",
        "AI_SEMICONDUCTOR",
    ])

    run_cmd([
        sys.executable,
        "-m",
        "app.batch.daily_backtest_run",
        "--date",
        dash_date,
        "--portfolio",
        "AI_SEMICONDUCTOR",
        "--capital",
        args.capital,
    ])

    print("\n[MCP 4.0 REAL DAILY COLLECT COMPLETE]", dash_date)


if __name__ == "__main__":
    main()
