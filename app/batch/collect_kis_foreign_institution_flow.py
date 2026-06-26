import argparse
from datetime import datetime

from sqlalchemy import text

from app.collectors.kis.client import kis_get
from app.core.database import SessionLocal


def to_int(v):
    if v is None:
        return 0
    try:
        return int(float(str(v).replace(",", "").strip()))
    except Exception:
        return 0


def pick(row, keys):
    for k in keys:
        if k in row:
            return row[k]
    return None


def load_foreign_institution_total(market_code="000"):
    """
    한국투자증권 국내기관_외국인 매매종목가집계
    market_code 후보:
    000 전체
    001 코스피
    101 코스닥
    """

    data = kis_get(
        path="/uapi/domestic-stock/v1/quotations/foreign-institution-total",
        tr_id="FHKST644400C0",
        params={
            "FID_COND_MRKT_DIV_CODE": "V",
            "FID_COND_SCR_DIV_CODE": "16449",
            "FID_INPUT_ISCD": market_code,
            "FID_DIV_CLS_CODE": "0",
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_ETC_CLS_CODE": "0",
        },
    )

    rows = []

    for key in ["output", "output1", "output2"]:
        value = data.get(key)
        if isinstance(value, list):
            rows.extend(value)

    return rows


def normalize_row(row):
    stock_code = str(pick(row, [
        "mksc_shrn_iscd",
        "stck_shrn_iscd",
        "pdno",
        "isu_cd",
    ]) or "").zfill(6)

    stock_name = pick(row, [
        "hts_kor_isnm",
        "prdt_name",
        "stck_prdt_name",
        "isu_abbrv",
    ])

    foreign_net = to_int(pick(row, [
        "frgn_ntby_qty",
        "frgn_ntby_tr_pbmn",
        "frgn_ntby_amt",
        "frgn_ntby_tr_amt",
    ]))

    institution_net = to_int(pick(row, [
        "orgn_ntby_qty",
        "orgn_ntby_tr_pbmn",
        "orgn_ntby_amt",
        "orgn_ntby_tr_amt",
    ]))

    return {
        "stock_code": stock_code,
        "stock_name": stock_name,
        "foreign_net": foreign_net,
        "institution_net": institution_net,
        "pension_net": 0,
        "program_net": 0,
    }


def save_rows(trade_date, rows):
    db = SessionLocal()
    saved = 0

    try:
        for raw in rows:
            r = normalize_row(raw)

            if not r["stock_code"] or r["stock_code"] == "000000":
                continue

            db.execute(text("""
                INSERT INTO mcp4.investor_flow_daily
                (
                    trade_date,
                    stock_code,
                    foreign_net,
                    institution_net,
                    pension_net,
                    program_net,
                    created_at
                )
                VALUES
                (
                    :trade_date,
                    :stock_code,
                    :foreign_net,
                    :institution_net,
                    :pension_net,
                    :program_net,
                    NOW()
                )
                ON CONFLICT (trade_date, stock_code)
                DO UPDATE SET
                    foreign_net = EXCLUDED.foreign_net,
                    institution_net = EXCLUDED.institution_net,
                    pension_net = EXCLUDED.pension_net,
                    program_net = EXCLUDED.program_net,
                    created_at = NOW()
            """), {
                "trade_date": trade_date,
                "stock_code": r["stock_code"],
                "foreign_net": r["foreign_net"],
                "institution_net": r["institution_net"],
                "pension_net": r["pension_net"],
                "program_net": r["program_net"],
            })

            saved += 1

        db.commit()

    finally:
        db.close()

    return saved


def run(bas_dd):
    trade_date = f"{bas_dd[0:4]}-{bas_dd[4:6]}-{bas_dd[6:8]}"

    all_rows = []

    for market_code in ["001", "101"]:
        try:
            rows = load_foreign_institution_total(market_code)
            print("[KIS FLOW] market:", market_code, "rows:", len(rows))
            all_rows.extend(rows)
        except Exception as e:
            print("[WARN] KIS market failed:", market_code, e)

    saved = save_rows(trade_date, all_rows)

    print("[KIS FOREIGN INSTITUTION FLOW]", trade_date, "saved:", saved)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    run(args.date)
