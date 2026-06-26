from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal
from app.api.v9_quote import get_quote

router = APIRouter(
    prefix="/api/v9",
    tags=["MCP 9.2 Target Check"]
)


@router.get("/target-check")
def target_check():

    db = SessionLocal()

    try:

        rows = db.execute(
            text("""
                SELECT *
                FROM mcp4.portfolio_position
            """)
        ).mappings().all()

        results = []

        for row in rows:

            quote = get_quote(row["stock_code"])

            if not quote.get("found"):
                continue

            current_price = quote["current_price"]
            target_price = float(row["target_price"] or 0)

            reached = current_price >= target_price

            results.append({
                "stock_code": row["stock_code"],
                "stock_name": row["stock_name"],
                "current_price": current_price,
                "target_price": target_price,
                "target_reached": reached,
                "gap_percent": round(
                    ((current_price / target_price) - 1) * 100,
                    2
                ) if target_price > 0 else None
            })

        reached_count = len(
            [x for x in results if x["target_reached"]]
        )

        return {
            "found": True,
            "version": "MCP 9.2",
            "target_reached_count": reached_count,
            "positions": results,
            "message": "목표가 체크 완료"
        }

    finally:
        db.close()
