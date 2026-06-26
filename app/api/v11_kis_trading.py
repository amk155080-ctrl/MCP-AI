from fastapi import APIRouter
from sqlalchemy import text
from datetime import date
from dotenv import load_dotenv
import os
import requests

from app.core.database import SessionLocal
from app.core.kis_token import get_kis_access_token

load_dotenv()

router = APIRouter(
    prefix="/api/v11/kis",
    tags=["MCP 11.3~11.7 KIS Trading"]
)

KIS_APP_KEY = os.getenv("KIS_APP_KEY")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET")
KIS_BASE_URL = os.getenv("KIS_BASE_URL", "https://openapi.koreainvestment.com:9443")
KIS_CANO = os.getenv("KIS_CANO")
KIS_ACNT_PRDT_CD = os.getenv("KIS_ACNT_PRDT_CD")


def to_int(value):
    try:
        return int(str(value).replace(",", "").strip())
    except:
        return 0


def get_headers(tr_id: str):
    token = get_kis_access_token()

    if not token.get("found"):
        return None, token

    return {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token['access_token']}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": tr_id,
        "custtype": "P"
    }, token


@router.get("/orderable")
def get_orderable_amount(stock_code: str = "005930", price: int = 0):
    if not KIS_CANO or not KIS_ACNT_PRDT_CD:
        return {
            "found": False,
            "version": "MCP 11.3",
            "message": ".env에 KIS_CANO 또는 KIS_ACNT_PRDT_CD가 없습니다."
        }

    headers, token = get_headers("TTTC8908R")

    if not headers:
        return {
            "found": False,
            "version": "MCP 11.3",
            "message": "KIS 토큰 준비 실패",
            "token": token
        }

    url = f"{KIS_BASE_URL}/uapi/domestic-stock/v1/trading/inquire-psbl-order"

    params = {
        "CANO": KIS_CANO,
        "ACNT_PRDT_CD": KIS_ACNT_PRDT_CD,
        "PDNO": stock_code,
        "ORD_UNPR": str(price),
        "ORD_DVSN": "01",
        "CMA_EVLU_AMT_ICLD_YN": "N",
        "OVRS_ICLD_YN": "N"
    }

    res = requests.get(url, headers=headers, params=params, timeout=10)
    data = res.json()

    return {
        "found": res.status_code == 200,
        "version": "MCP 11.3",
        "status_code": res.status_code,
        "rt_cd": data.get("rt_cd"),
        "msg_cd": data.get("msg_cd"),
        "msg1": data.get("msg1"),
        "output": data.get("output"),
        "message": "주문 가능 금액 조회 완료"
    }


@router.get("/mock-order/{order_id}")
def mock_order(order_id: int):
    db = SessionLocal()

    try:
        row = db.execute(
            text("""
                SELECT *
                FROM mcp4.order_queue
                WHERE id = :id
            """),
            {"id": order_id}
        ).mappings().first()

        if not row:
            return {
                "found": False,
                "version": "MCP 11.4",
                "message": "주문 큐를 찾을 수 없습니다."
            }

        if row["status"] != "APPROVED":
            return {
                "found": False,
                "version": "MCP 11.4",
                "order_id": order_id,
                "status": row["status"],
                "message": "APPROVED 상태의 주문만 모의주문 가능합니다."
            }

        return {
            "found": True,
            "version": "MCP 11.4",
            "order_id": order_id,
            "stock_code": row["stock_code"],
            "stock_name": row["stock_name"],
            "action": row["action"],
            "quantity": row["quantity"],
            "price": float(row["current_price"] or 0),
            "status": "MOCK_READY",
            "message": "모의주문 검증 완료"
        }

    finally:
        db.close()


@router.post("/place-order/{order_id}")
def place_order(order_id: int):
    db = SessionLocal()

    try:
        row = db.execute(
            text("""
                SELECT *
                FROM mcp4.order_queue
                WHERE id = :id
            """),
            {"id": order_id}
        ).mappings().first()

        if not row:
            return {
                "ordered": False,
                "version": "MCP 11.5",
                "message": "주문 큐를 찾을 수 없습니다."
            }

        if row["status"] != "APPROVED":
            return {
                "ordered": False,
                "version": "MCP 11.5",
                "order_id": order_id,
                "status": row["status"],
                "message": "APPROVED 상태의 주문만 실주문 가능합니다."
            }

        action = row["action"]
        stock_code = row["stock_code"]
        quantity = int(row["quantity"] or 0)
        price = int(float(row["current_price"] or 0))

        if quantity <= 0:
            return {
                "ordered": False,
                "version": "MCP 11.5",
                "message": "주문 수량이 0 이하입니다."
            }

        if action == "SELL" or action == "TAKE_PROFIT":
            tr_id = "TTTC0801U"
        elif action == "BUY":
            tr_id = "TTTC0802U"
        else:
            return {
                "ordered": False,
                "version": "MCP 11.5",
                "message": f"지원하지 않는 action입니다: {action}"
            }

        headers, token = get_headers(tr_id)

        if not headers:
            return {
                "ordered": False,
                "version": "MCP 11.5",
                "message": "KIS 토큰 준비 실패",
                "token": token
            }

        url = f"{KIS_BASE_URL}/uapi/domestic-stock/v1/trading/order-cash"

        payload = {
            "CANO": KIS_CANO,
            "ACNT_PRDT_CD": KIS_ACNT_PRDT_CD,
            "PDNO": stock_code,
            "ORD_DVSN": "01",
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price)
        }

        res = requests.post(url, headers=headers, json=payload, timeout=10)
        data = res.json()

        rt_cd = data.get("rt_cd")
        msg_cd = data.get("msg_cd")
        msg1 = data.get("msg1")
        output = data.get("output") or {}

        kis_order_no = output.get("ODNO")
        kis_order_time = output.get("ORD_TMD")

        order_status = "ORDERED" if rt_cd == "0" else "FAILED"

        db.execute(
            text("""
                INSERT INTO mcp4.kis_order_log (
                    order_queue_id,
                    order_date,
                    stock_code,
                    stock_name,
                    action,
                    quantity,
                    price,
                    kis_order_no,
                    kis_order_time,
                    rt_cd,
                    msg_cd,
                    msg1,
                    status,
                    raw_response
                )
                VALUES (
                    :order_queue_id,
                    :order_date,
                    :stock_code,
                    :stock_name,
                    :action,
                    :quantity,
                    :price,
                    :kis_order_no,
                    :kis_order_time,
                    :rt_cd,
                    :msg_cd,
                    :msg1,
                    :status,
                    CAST(:raw_response AS JSONB)
                )
            """),
            {
                "order_queue_id": order_id,
                "order_date": date.today(),
                "stock_code": stock_code,
                "stock_name": row["stock_name"],
                "action": action,
                "quantity": quantity,
                "price": price,
                "kis_order_no": kis_order_no,
                "kis_order_time": kis_order_time,
                "rt_cd": rt_cd,
                "msg_cd": msg_cd,
                "msg1": msg1,
                "status": order_status,
                "raw_response": __import__("json").dumps(data, ensure_ascii=False)
            }
        )

        if rt_cd == "0":
            db.execute(
                text("""
                    UPDATE mcp4.order_queue
                    SET status = 'ORDERED'
                    WHERE id = :id
                """),
                {"id": order_id}
            )

        db.commit()

        return {
            "ordered": rt_cd == "0",
            "version": "MCP 11.5",
            "order_id": order_id,
            "kis_order_no": kis_order_no,
            "kis_order_time": kis_order_time,
            "rt_cd": rt_cd,
            "msg_cd": msg_cd,
            "msg1": msg1,
            "status": order_status,
            "response": data,
            "message": "KIS 실주문 요청 완료"
        }

    finally:
        db.close()


@router.get("/fills")
def get_fills():
    headers, token = get_headers("TTTC8001R")

    if not headers:
        return {
            "found": False,
            "version": "MCP 11.6",
            "message": "KIS 토큰 준비 실패",
            "token": token
        }

    url = f"{KIS_BASE_URL}/uapi/domestic-stock/v1/trading/inquire-daily-ccld"

    params = {
        "CANO": KIS_CANO,
        "ACNT_PRDT_CD": KIS_ACNT_PRDT_CD,
        "INQR_STRT_DT": date.today().strftime("%Y%m%d"),
        "INQR_END_DT": date.today().strftime("%Y%m%d"),
        "SLL_BUY_DVSN_CD": "00",
        "INQR_DVSN": "00",
        "PDNO": "",
        "CCLD_DVSN": "00",
        "ORD_GNO_BRNO": "",
        "ODNO": "",
        "INQR_DVSN_3": "00",
        "INQR_DVSN_1": "",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }

    res = requests.get(url, headers=headers, params=params, timeout=10)
    data = res.json()

    return {
        "found": res.status_code == 200,
        "version": "MCP 11.6",
        "status_code": res.status_code,
        "rt_cd": data.get("rt_cd"),
        "msg_cd": data.get("msg_cd"),
        "msg1": data.get("msg1"),
        "output1": data.get("output1"),
        "output2": data.get("output2"),
        "message": "KIS 체결 조회 완료"
    }


@router.get("/order-logs")
def get_kis_order_logs(limit: int = 50):
    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT *
                FROM mcp4.kis_order_log
                ORDER BY id DESC
                LIMIT :limit
            """),
            {"limit": limit}
        ).mappings().all()

        return {
            "found": True,
            "version": "MCP 11.7",
            "count": len(rows),
            "items": [dict(row) for row in rows],
            "message": "KIS 주문 로그 조회 완료"
        }

    finally:
        db.close()
