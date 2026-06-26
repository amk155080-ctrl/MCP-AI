import argparse
from datetime import datetime

from pykrx import stock
from sqlalchemy import text

from app.core.database import SessionLocal


SEMICONDUCTOR_STOCKS = {
    "000660": "SK하이닉스",
    "005930": "삼성전자",
    "042700": "한미반도체",
    "089030": "테크윙",
    "095340": "ISC",
    "039030": "이오테크닉스",
    "058470": "리노공업",
    "403870": "HPSP",
    "240810": "원익IPS",
    "036930": "주성엔지니어링",
    "319660": "피에스케이",
    "084370": "유진테크",
    "067310": "하나마이크론",
    "222800": "심텍",
}


def to_int(value):
    try:
        return int(value)
    except Exception:
        return 0


def to_float(value):
    try:
        return float(value)
    except Exception:
        return 0.0


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
    # 대차 데이터가 아직 없으면 중립 55점
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


def run(bas_dd):
    trade_date = f"{bas_dd[0:4]}-{bas_dd[4:6]}-{bas_dd[6:8]}"

    df = stock.get_shorting_status_by_date(
        bas_dd,
        bas_dd,
        "KOSPI"
    )

    df_kosdaq = stock.get_shorting_status_by_date(
        bas_dd,
        bas_dd,
        "KOSDAQ"
    )

    import pandas as pd
    df_all = pd.concat([df, df_kosdaq])

    db = SessionLocal()
    saved = 0

    try:
        for stock_code, row in df_all.iterrows():
            stock_code = str(stock_code).zfill(6)

            if stock_code not in SEMICONDUCTOR_STOCKS:
                continue

            short_amount = to_int(row.get("거래대금", 0))
            short_volume = to_int(row.get("거래량", 0))
            short_ratio = to_float(row.get("비중", 0))

            loan_balance = 0
            loan_change = 0

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
                    "stock_name": SEMICONDUCTOR_STOCKS[stock_code],
                    "short_amount": short_amount,
                    "short_ratio": short_ratio,
                    "loan_balance": loan_balance,
                    "loan_change": loan_change,
                    "short_score": short_score,
                    "loan_score": loan_score,
                    "total_score": total_score,
                    "memo": "pykrx 공매도 실제 수집 + 대차잔고 중립값",
                },
            )

            saved += 1

        db.commit()

    finally:
        db.close()

    print("[PYKRX SHORT]", trade_date, "saved:", saved)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    run(args.date)
