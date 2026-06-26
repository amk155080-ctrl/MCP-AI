from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal
from app.api.v9_quote import get_quote

router = APIRouter(
    prefix="/api/v9",
    tags=["MCP 9.3 Stop Check"]
)


@router.get("/stop-check")
def stop_check():

    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT *
                FROM mcp4.portfolio_position
                ORDER BY id ASC
            """)
        ).mappings().all()

        results = []

        for row in rows:
            quote = get_quote(row["stock_code"])

            if not quote.get("found"):
                results.append({
                    "stock_code": row["stock_code"],
                    "stock_name": row["stock_name"],
                    "found": False,
                    "message": "시세 조회 실패"
                })
                continue

            current_price = quote["current_price"]
            stop_price = float(row["stop_price"] or 0)

            if stop_price <= 0:
                stop_broken = False
                gap_percent = None
                status = "NO_STOP_PRICE"
                action = "손절가 미설정"
            else:
                stop_broken = current_price <= stop_price
                gap_percent = round(((current_price / stop_price) - 1) * 100, 2)

                if stop_broken:
                    status = "STOP_BROKEN"
                    action = "손절 검토 필요"
                else:
                    status = "SAFE"
                    action = "보유 가능"

            results.append({
                "stock_code": row["stock_code"],
                "stock_name": row["stock_name"],
                "current_price": current_price,
                "stop_price": stop_price,
                "stop_broken": stop_broken,
                "gap_percent": gap_percent,
                "status": status,
                "action": action,
                "quote_base_date": quote.get("base_date"),
                "quote_source": quote.get("source")
            })

        stop_broken_count = len([x for x in results if x.get("stop_broken")])

        if stop_broken_count > 0:
            alert_level = "WARNING"
            message = "손절가 이탈 종목이 있습니다."
        else:
            alert_level = "NORMAL"
            message = "손절가 이탈 종목이 없습니다."

        return {
            "found": True,
            "version": "MCP 9.3",
            "alert_level": alert_level,
            "stop_broken_count": stop_broken_count,
            "positions": results,
            "message": message
        }

    finally:
        db.close()
