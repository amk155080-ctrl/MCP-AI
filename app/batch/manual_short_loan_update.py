import argparse
from sqlalchemy import text
from app.core.database import SessionLocal


def calc_short_score(short_ratio):
    if short_ratio <= 1:
        return 90
    if short_ratio <= 2:
        return 80
    if short_ratio <= 3:
        return 70
    if short_ratio <= 5:
        return 55
    if short_ratio <= 8:
        return 40
    return 25


def calc_loan_score(loan_change):
    # 대차잔고 감소는 숏커버 가능성으로 가점
    if loan_change <= -50000000000:
        return 90
    if loan_change <= -10000000000:
        return 80
    if loan_change < 0:
        return 70
    if loan_change == 0:
        return 55
    if loan_change <= 10000000000:
        return 45
    return 30


def run(trade_date):
    rows = [
        # stock_code, stock_name, short_amount, short_ratio, loan_balance, loan_change
        ("000660", "SK하이닉스", 45000000000, 1.2, 850000000000, -80000000000),
        ("042700", "한미반도체", 12000000000, 1.6, 180000000000, -25000000000),
        ("005930", "삼성전자", 70000000000, 2.3, 1200000000000, -30000000000),
        ("095340", "ISC", 6000000000, 2.1, 90000000000, -8000000000),
        ("089030", "테크윙", 5000000000, 2.8, 70000000000, -5000000000),
        ("039030", "이오테크닉스", 8000000000, 3.2, 110000000000, 5000000000),
    ]

    db = SessionLocal()

    try:
        for stock_code, stock_name, short_amount, short_ratio, loan_balance, loan_change in rows:
            short_score = calc_short_score(short_ratio)
            loan_score = calc_loan_score(loan_change)

            total_score = round(
                short_score * 0.55 +
                loan_score * 0.45,
                2,
            )

            db.execute(
                text(
                    """
                    INSERT INTO mcp4.short_loan_daily
                    (
                        trade_date,
                        stock_code,
                        stock_name,
                        short_amount,
                        short_ratio,
                        loan_balance,
                        loan_change,
                        short_score,
                        loan_score,
                        total_score,
                        memo
                    )
                    VALUES
                    (
                        :trade_date,
                        :stock_code,
                        :stock_name,
                        :short_amount,
                        :short_ratio,
                        :loan_balance,
                        :loan_change,
                        :short_score,
                        :loan_score,
                        :total_score,
                        :memo
                    )
                    ON CONFLICT (trade_date, stock_code)
                    DO UPDATE SET
                        stock_name = EXCLUDED.stock_name,
                        short_amount = EXCLUDED.short_amount,
                        short_ratio = EXCLUDED.short_ratio,
                        loan_balance = EXCLUDED.loan_balance,
                        loan_change = EXCLUDED.loan_change,
                        short_score = EXCLUDED.short_score,
                        loan_score = EXCLUDED.loan_score,
                        total_score = EXCLUDED.total_score,
                        memo = EXCLUDED.memo
                    """
                ),
                {
                    "trade_date": trade_date,
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "short_amount": short_amount,
                    "short_ratio": short_ratio,
                    "loan_balance": loan_balance,
                    "loan_change": loan_change,
                    "short_score": short_score,
                    "loan_score": loan_score,
                    "total_score": total_score,
                    "memo": "공매도·대차잔고 수동 입력 기반 점수",
                },
            )

        db.commit()

    finally:
        db.close()

    print("[SHORT LOAN]", trade_date, "saved")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    run(args.date)
