from fastapi import APIRouter
from pykrx import stock
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import requests

load_dotenv()

router = APIRouter(prefix="/api/v9", tags=["MCP 9.0 KRX Quote"])

KRX_API_KEY = os.getenv("KRX_API_KEY")


def get_recent_business_dates(days=10):
    today = datetime.now()
    return [(today - timedelta(days=i)).strftime("%Y%m%d") for i in range(days)]


def to_int(value):
    try:
        return int(str(value).replace(",", "").replace("+", "").strip())
    except:
        return None


def to_float(value):
    try:
        return float(str(value).replace(",", "").replace("+", "").replace("%", "").strip())
    except:
        return None


@router.get("/quote/{stock_code}")
def get_quote(stock_code: str):
    stock_name = stock.get_market_ticker_name(stock_code)

    url = "http://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd.json"
    headers = {"AUTH_KEY": KRX_API_KEY}

    for bas_dd in get_recent_business_dates(10):
        response = requests.get(url, headers=headers, params={"basDd": bas_dd}, timeout=10)
        data = response.json()
        rows = data.get("OutBlock_1", [])

        for row in rows:
            if row.get("ISU_CD") == stock_code:
                return {
                    "found": True,
                    "version": "MCP 9.0",
                    "source": "KRX Open API",
                    "base_date": bas_dd,
                    "stock_code": stock_code,
                    "stock_name": row.get("ISU_NM") or stock_name,
                    "market": row.get("MKT_NM"),
                    "current_price": to_int(row.get("TDD_CLSPRC")),
                    "change_price": to_int(row.get("CMPPREVDD_PRC")),
                    "change_rate": to_float(row.get("FLUC_RT")),
                    "open_price": to_int(row.get("TDD_OPNPRC")),
                    "high_price": to_int(row.get("TDD_HGPRC")),
                    "low_price": to_int(row.get("TDD_LWPRC")),
                    "volume": to_int(row.get("ACC_TRDVOL")),
                    "trading_value": to_int(row.get("ACC_TRDVAL")),
                    "market_cap": to_int(row.get("MKTCAP")),
                    "listed_shares": to_int(row.get("LIST_SHRS")),
                    "message": "KRX 시세 조회 성공"
                }

    return {
        "found": False,
        "version": "MCP 9.0",
        "stock_code": stock_code,
        "stock_name": stock_name,
        "message": "최근 10일 내 KRX 시세 데이터를 찾지 못했습니다."
    }
