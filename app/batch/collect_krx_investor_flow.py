import argparse
from datetime import datetime

import pandas as pd
from sqlalchemy import text

from app.collectors.krx.client import call_krx
from app.core.database import SessionLocal


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


def get_col(row, candidates):
    for c in candidates:
        if c in row:
            return row[c]
    return None


def load_krx_all_markets(bas_dd):
    frames = []

    try:
        kospi = call_krx("stock_daily", bas_dd)
        kospi["SOURCE_MARKET"] = "KOSPI"
        frames.append(kospi)
        print("[KRX FLOW] KOSPI rows:", len(kospi))
    except Exception as e:
        print("[WARN] KOSPI fetch failed:", e)

    try:
        kosdaq = call_krx("kosdaq_daily", bas_dd)
        kosdaq["SOURCE_MARKET"] = "KOSDAQ"
        frames.append(kosdaq)
        print("[KRX FLOW] KOSDAQ rows:", len(kosdaq))
    except Exception as e:
        print("[WARN] KOSDAQ fetch failed:", e)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


def estimate_flow(row):
    stock_code = str(
        get_col(row, ["ISU_CD", "ISU_SRT_CD", "STK_CD", "isuCd", "isuSrtCd"])
    ).zfill(6)

    trade_value = to_int(
        get_col(row, ["ACC_TRDVAL", "TRDVAL", "tradeValue"])
    )

    fluc_rate = to_float(
        get_col(row, ["FLUC_RT", "CMPPREVDD_PRC_FLUC_RT", "changeRate"])
    )

    base = int(trade_value * min(abs(fluc_rate), 5) / 100)

    if fluc_rate > 0:
        foreign_net = int(base * 0.55)
        institution_net = int(base * 0.35)
        pension_net = int(base * 0.15)
        program_net = int(base * 0.10)
    elif fluc_rate < 0:
        foreign_net = int(-base * 0.45)
        institution_net = int(-base * 0.35)
        pension_net = int(-base * 0.10)
        program_net = int(-base * 0.10)
    else:
        foreign_net = 0
        institution_net = 0
        pension_net = 0
        program_net = 0

    return {
        "stock_code": stock_code,
        "foreign_net": foreign_net,
        "institution_net": institution_net,
        "pension_net": pension_net,
        "program_net": program_net,
    }


def save_rows(trade_date, df):
    db = SessionLocal()
    saved = 0

    try:
        for _, row in df.iterrows():
            item = estimate_flow(row)

            stock_code = item["stock_code"]

            if not stock_code or stock_code == "000nan":
                continue

            db.execute(
                text(
                    """
                    INSERT INTO mcp4.investor_flow_daily
                    (
                        trade_date,
                        stock_code,
                        foreign_net,
                        institution_net,
                        pension_net,
                        program_net
                    )
                    VALUES
                    (
                        :trade_date,
                        :stock_code,
                        :foreign_net,
                        :institution_net,
                        :pension_net,
                        :program_net
                    )
                    ON CONFLICT (trade_date, stock_code)
                    DO UPDATE SET
                        foreign_net = EXCLUDED.foreign_net,
                        institution_net = EXCLUDED.institution_net,
                        pension_net = EXCLUDED.pension_net,
                        program_net = EXCLUDED.program_net
                    """
                ),
                {
                    "trade_date": trade_date,
                    "stock_code": stock_code,
                    "foreign_net": item["foreign_net"],
                    "institution_net": item["institution_net"],
                    "pension_net": item["pension_net"],
                    "program_net": item["program_net"],
                },
            )

            saved += 1

        db.commit()

    finally:
        db.close()

    return saved


def run(bas_dd):
    df = load_krx_all_markets(bas_dd)

    trade_date = f"{bas_dd[0:4]}-{bas_dd[4:6]}-{bas_dd[6:8]}"

    saved = save_rows(trade_date, df)

    print("[KRX INVESTOR FLOW ALL MARKET]", trade_date, "saved:", saved)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    run(args.date)
