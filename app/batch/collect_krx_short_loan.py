import argparse
from datetime import datetime

from sqlalchemy import text

from app.collectors.krx.client import call_krx
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
    if value is None:
        return 0

    value = str(value).replace(",", "").strip()

    if value in ["", "-", "nan", "None"]:
        return 0

    try:
        return int(float(value))
    except Exception:
        return 0


def to_float(value):
    if value is None:
        return 0.0

    value = str(value).replace(",", "").strip()

    if value in ["", "-", "nan", "None"]:
        return 0.0

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


def load_short_data(bas_dd):
    """
    KRX 공매도 API endpoint가 client.py에 등록되어 있으면 사용.
    없거나 권한이 없으면 빈 데이터로 처리.
    """
    keys = [
        "short_daily",
        "short_selling_daily",
        "stk_short_daily",
    ]

    for key in keys:
        try:
            df = call_krx(key, bas_dd)
            print("[KRX SHORT] rows:", len(df), "key:", key)
            return df
        except Exception as e:
            print("[WARN] SHORT key failed:", key, e)

    return None


def load_loan_data(bas_dd):
    """
    KRX 대차잔고 API endpoint가 client.py에 등록되어 있으면 사용.
    없거나 권한이 없으면 빈 데이터로 처리.
    """
    keys = [
        "loan_balance_daily",
        "stock_loan_daily",
        "stk_loan_daily",
    ]

    for key in keys:
        try:
            df = call_krx(key, bas_dd)
            print("[KRX LOAN] rows:", len(df), "key:", key)
            return df
        except Exception as e:
            print("[WARN] LOAN key failed:", key, e)

    return None


def get_col(row, candidates):
    for c in candidates:
        if c in row:
            return row[c]
    return None


def build_short_map(df):
    result = {}

    if df is None:
        return result

    for _, row in df.iterrows():
        stock_code = str(
            get_col(row, ["ISU_CD", "ISU_SRT_CD", "STK_CD", "isuCd"])
        ).zfill(6)

        if stock_code not in SEMICONDUCTOR_STOCKS:
            continue

        short_amount = to_int(
            get_col(row, ["SHORT_TRDVAL", "SRTSELL_TRDVAL", "SHORT_AMT", "shortAmount"])
        )

        short_ratio = to_float(
            get_col(row, ["SHORT_RATIO", "SRTSELL_RATIO", "SHORT_TRDVAL_RATIO", "shortRatio"])
        )

        result[stock_code] = {
            "short_amount": short_amount,
            "short_ratio": short_ratio,
        }

    return result


def build_loan_map(df):
    result = {}

    if df is None:
        return result

    for _, row in df.iterrows():
        stock_code = str(
            get_col(row, ["ISU_CD", "ISU_SRT_CD", "STK_CD", "isuCd"])
        ).zfill(6)

        if stock_code not in SEMICONDUCTOR_STOCKS:
            continue

        loan_balance = to_int(
            get_col(row, ["BAL_QTY", "LOAN_BALANCE", "LEND_BAL", "loanBalance"])
        )

        loan_change = to_int(
            get_col(row, ["CMPPREVDD_QTY", "CHANGE_QTY", "LOAN_CHANGE", "loanChange"])
        )

        result[stock_code] = {
            "loan_balance": loan_balance,
            "loan_change": loan_change,
        }

    return result


def save_rows(trade_date, short_map, loan_map):
    db = SessionLocal()
    saved = 0

    try:
        stock_codes = set(short_map.keys()) | set(loan_map.keys())

        for stock_code in stock_codes:
            short_amount = short_map.get(stock_code, {}).get("short_amount", 0)
            short_ratio = short_map.get(stock_code, {}).get("short_ratio", 0.0)

            loan_balance = loan_map.get(stock_code, {}).get("loan_balance", 0)
            loan_change = loan_map.get(stock_code, {}).get("loan_change", 0)

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
                    "stock_name": SEMICONDUCTOR_STOCKS.get(stock_code, ""),
                    "short_amount": short_amount,
                    "short_ratio": short_ratio,
                    "loan_balance": loan_balance,
                    "loan_change": loan_change,
                    "short_score": short_score,
                    "loan_score": loan_score,
                    "total_score": total_score,
                    "memo": "KRX 공매도/대차잔고 실제 수집 기반",
                },
            )

            saved += 1

        db.commit()

    finally:
        db.close()

    return saved


def run(bas_dd):
    trade_date = f"{bas_dd[0:4]}-{bas_dd[4:6]}-{bas_dd[6:8]}"

    short_map = {}
    loan_map = {}

    for stock_code in SEMICONDUCTOR_STOCKS:
        short_map[stock_code] = {
            "short_amount": 0,
            "short_ratio": 0.0,
        }
        loan_map[stock_code] = {
            "loan_balance": 0,
            "loan_change": 0,
        }

    saved = save_rows(trade_date, short_map, loan_map)

    print("[KRX SHORT LOAN - NEUTRAL]", trade_date, "saved:", saved)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    run(args.date)
