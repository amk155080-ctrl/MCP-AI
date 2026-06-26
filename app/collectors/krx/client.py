import requests
import pandas as pd
from app.core.config import settings

BASE = "https://data-dbg.krx.co.kr/svc/apis"

ENDPOINTS = {
    "stock_daily": f"{BASE}/sto/stk_bydd_trd",
    "kosdaq_daily": f"{BASE}/sto/ksq_bydd_trd",

    "stock_base": f"{BASE}/sto/stk_isu_base_info",
    "kospi_index": f"{BASE}/idx/kospi_dd_trd",
    "kosdaq_index": f"{BASE}/idx/kosdaq_dd_trd",

    # Short / Loan 후보 endpoint
    "short_daily": f"{BASE}/sto/stk_srt_bydd_trd",
    "loan_balance_daily": f"{BASE}/sto/stk_lend_bydd_bal",
}

def call_krx(endpoint_key: str, bas_dd: str) -> pd.DataFrame:
    if not settings.KRX_API_KEY:
        raise RuntimeError("KRX_API_KEY가 .env에 없습니다.")

    url = ENDPOINTS[endpoint_key]
    headers = {
        "AUTH_KEY": settings.KRX_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {"basDd": bas_dd}

    r = requests.post(url, headers=headers, json=payload, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"KRX 호출 실패 {r.status_code}: {r.text}")

    data = r.json()
    return pd.DataFrame(data.get("OutBlock_1", []))
