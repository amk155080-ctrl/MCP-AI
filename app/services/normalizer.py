import pandas as pd
from decimal import Decimal, InvalidOperation

def to_num(value):
    if value is None:
        return None
    s = str(value).replace(",", "").strip()
    if s in ("", "-", "nan", "None"):
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        return None

def krx_stock_daily_to_records(df: pd.DataFrame):
    records = []
    for _, r in df.iterrows():
        records.append({
            "trade_date": pd.to_datetime(r["BAS_DD"]).date(),
            "stock_code": r.get("ISU_CD"),
            "stock_name": r.get("ISU_NM"),
            "open_price": to_num(r.get("TDD_OPNPRC")),
            "high_price": to_num(r.get("TDD_HGPRC")),
            "low_price": to_num(r.get("TDD_LWPRC")),
            "close_price": to_num(r.get("TDD_CLSPRC")),
            "change_amount": to_num(r.get("CMPPREVDD_PRC")),
            "change_rate": to_num(r.get("FLUC_RT")),
            "volume": int(to_num(r.get("ACC_TRDVOL")) or 0),
            "trade_value": to_num(r.get("ACC_TRDVAL")),
            "market_cap": to_num(r.get("MKTCAP")),
            "listed_shares": int(to_num(r.get("LIST_SHRS")) or 0),
        })
    return records
