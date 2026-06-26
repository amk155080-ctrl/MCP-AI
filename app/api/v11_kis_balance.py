from fastapi import APIRouter
from dotenv import load_dotenv
import os
import requests

from app.core.kis_token import get_kis_access_token

load_dotenv()

router = APIRouter(
    prefix="/api/v11/kis",
    tags=["MCP 11.1 KIS Balance"]
)

KIS_APP_KEY = os.getenv("KIS_APP_KEY")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET")
KIS_BASE_URL = os.getenv("KIS_BASE_URL", "https://openapi.koreainvestment.com:9443")
KIS_CANO = os.getenv("KIS_CANO")
KIS_ACNT_PRDT_CD = os.getenv("KIS_ACNT_PRDT_CD")


@router.get("/balance")
def get_kis_balance():
    if not KIS_CANO or not KIS_ACNT_PRDT_CD:
        return {
            "found": False,
            "version": "MCP 11.1",
            "message": ".env에 KIS_CANO 또는 KIS_ACNT_PRDT_CD가 없습니다."
        }

    token_result = get_kis_access_token()

    if not token_result.get("found"):
        return {
            "found": False,
            "version": "MCP 11.1",
            "message": "KIS 토큰 준비 실패",
            "token_result": token_result
        }

    access_token = token_result.get("access_token")

    if not access_token:
        return {
            "found": False,
            "version": "MCP 11.1",
            "message": "access_token을 가져오지 못했습니다.",
            "response": token_data
        }

    url = f"{KIS_BASE_URL}/uapi/domestic-stock/v1/trading/inquire-balance"

    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": "TTTC8434R",
        "custtype": "P"
    }

    params = {
        "CANO": KIS_CANO,
        "ACNT_PRDT_CD": KIS_ACNT_PRDT_CD,
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "01",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10
        )

        data = response.json()

        if response.status_code != 200:
            return {
                "found": False,
                "version": "MCP 11.1",
                "status_code": response.status_code,
                "response": data,
                "message": "KIS 계좌 잔고 조회 실패"
            }

        return {
            "found": True,
            "version": "MCP 11.1",
            "status_code": response.status_code,
            "rt_cd": data.get("rt_cd"),
            "msg_cd": data.get("msg_cd"),
            "msg1": data.get("msg1"),
            "output1": data.get("output1"),
            "output2": data.get("output2"),
            "message": "KIS 계좌 잔고 조회 완료"
        }

    except Exception as e:
        return {
            "found": False,
            "version": "MCP 11.1",
            "error": str(e),
            "message": "KIS 계좌 잔고 조회 중 오류 발생"
        }
