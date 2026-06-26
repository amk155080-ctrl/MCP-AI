import argparse
from datetime import datetime

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


def normalize_rows(df, market_type):
    rows = []

    for _, row in df.iterrows():
        stock_code = str(
            get_col(row, ["ISU_SRT_CD", "ISU_CD", "STK_CD", "isuSrtCd"])
        ).zfill(6)

        stock_name = get_col(row, ["ISU_ABBRV", "ISU_NM", "isuAbrv", "isuNm"])

        if not stock_code or stock_code == "000nan" or not stock_name:
            continue

        close_price = to_float(
            get_col(row, ["TDD_CLSPRC", "CLSPRC", "closePrice"])
        )

        open_price = to_float(
            get_col(row, ["TDD_OPNPRC", "OPNPRC", "openPrice"])
        )

        high_price = to_float(
            get_col(row, ["TDD_HGPRC", "HGPRC", "highPrice"])
        )

        low_price = to_float(
            get_col(row, ["TDD_LWPRC", "LWPRC", "lowPrice"])
        )

        change_amount = to_float(
            get_col(row, ["CMPPREVDD_PRC", "FLUC_TP_CD", "changeAmount"])
        )

        change_rate = to_float(
            get_col(row, ["FLUC_RT", "CMPPREVDD_PRC_FLUC_RT", "changeRate"])
        )

        volume = to_int(
            get_col(row, ["ACC_TRDVOL", "TRDVOL", "volume"])
        )

        trade_value = to_float(
            get_col(row, ["ACC_TRDVAL", "TRDVAL", "tradeValue"])
        )

        market_cap = to_float(
            get_col(row, ["MKTCAP", "marketCap"])
        )

        listed_shares = to_int(
            get_col(row, ["LIST_SHRS", "listedShares"])
        )

        rows.append({
            "stock_code": stock_code,
            "stock_name": str(stock_name).strip(),
            "market_type": market_type,
            "open_price": open_price,
            "high_price": high_price,
            "low_price": low_price,
            "close_price": close_price,
            "change_amount": change_amount,
            "change_rate": change_rate,
            "volume": volume,
            "trade_value": trade_value,
            "market_cap": market_cap,
            "listed_shares": listed_shares,
        })

    return rows


def save_rows(trade_date, rows):
    db = SessionLocal()
    saved = 0

    try:
        for r in rows:
            db.execute(text("""
                INSERT INTO mcp4.stock_price_daily
                (
                    trade_date,
                    stock_code,
                    stock_name,
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    change_amount,
                    change_rate,
                    volume,
                    trade_value,
                    market_cap,
                    listed_shares,
                    created_at
                )
                VALUES
                (
                    :trade_date,
                    :stock_code,
                    :stock_name,
                    :open_price,
                    :high_price,
                    :low_price,
                    :close_price,
                    :change_amount,
                    :change_rate,
                    :volume,
                    :trade_value,
                    :market_cap,
                    :listed_shares,
                    NOW()
                )
                ON CONFLICT (trade_date, stock_code)
                DO UPDATE SET
                    stock_name = EXCLUDED.stock_name,
                    open_price = EXCLUDED.open_price,
                    high_price = EXCLUDED.high_price,
                    low_price = EXCLUDED.low_price,
                    close_price = EXCLUDED.close_price,
                    change_amount = EXCLUDED.change_amount,
                    change_rate = EXCLUDED.change_rate,
                    volume = EXCLUDED.volume,
                    trade_value = EXCLUDED.trade_value,
                    market_cap = EXCLUDED.market_cap,
                    listed_shares = EXCLUDED.listed_shares
            """), {
                "trade_date": trade_date,
                **r,
            })
            saved += 1

        db.commit()

    finally:
        db.close()

    return saved


def update_stock_master(rows):
    db = SessionLocal()
    saved = 0

    try:
        for r in rows:
            db.execute(text("""
                INSERT INTO mcp4.stock_master
                (
                    stock_code,
                    stock_name,
                    market_type,
                    sector_name,
                    listing_date,
                    listing_shares,
                    created_at,
                    updated_at
                )
                VALUES
                (
                    :stock_code,
                    :stock_name,
                    :market_type,
                    NULL,
                    NULL,
                    :listing_shares,
                    NOW(),
                    NOW()
                )
                ON CONFLICT (stock_code)
                DO UPDATE SET
                    stock_name = EXCLUDED.stock_name,
                    market_type = EXCLUDED.market_type,
                    listing_shares = EXCLUDED.listing_shares,
                    updated_at = NOW()
            """), {
                "stock_code": r["stock_code"],
                "stock_name": r["stock_name"],
                "market_type": r["market_type"],
                "listing_shares": r["listed_shares"],
            })
            saved += 1

        db.commit()

    finally:
        db.close()

    return saved


def run(bas_dd):
    trade_date = f"{bas_dd[0:4]}-{bas_dd[4:6]}-{bas_dd[6:8]}"

    all_rows = []

    kospi_df = call_krx("stock_daily", bas_dd)
    kospi_rows = normalize_rows(kospi_df, "KOSPI")
    print("[KRX PRICE] KOSPI rows:", len(kospi_rows))
    all_rows.extend(kospi_rows)

    kosdaq_df = call_krx("kosdaq_daily", bas_dd)
    kosdaq_rows = normalize_rows(kosdaq_df, "KOSDAQ")
    print("[KRX PRICE] KOSDAQ rows:", len(kosdaq_rows))
    all_rows.extend(kosdaq_rows)

    saved_price = save_rows(trade_date, all_rows)
    saved_master = update_stock_master(all_rows)

    print("[KRX PRICE ALL]", trade_date, "price_saved:", saved_price, "master_saved:", saved_master)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    run(args.date)
