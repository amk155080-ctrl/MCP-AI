from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@router.get("/dashboard/stock/{stock_code}")
def stock_detail(
    request: Request,
    stock_code: str
):
    db = SessionLocal()

    try:
        row = db.execute(text("""
            SELECT
                stock_code,
                stock_name,
                total_score,
                risk_score,
                confidence,
                signal,
                target_price,
                stop_loss,
                smart_money_net
            FROM mcp4.recommendation_history
            WHERE stock_code = :stock_code
            ORDER BY trade_date DESC
            LIMIT 1
        """), {
            "stock_code": stock_code
        }).mappings().first()

        if not row:
            return {
                "found": False,
                "message": "종목 없음"
            }

        total_score = float(row["total_score"] or 0)
        risk_score = float(row["risk_score"] or 0)
        confidence = float(row["confidence"] or 0)

        committee_score = round(
            total_score * 0.5 +
            risk_score * 0.2 +
            confidence * 0.3,
            2
        )

        target_price = float(row["target_price"] or 0)
        stop_loss = float(row["stop_loss"] or 0)

        entry_price = target_price / 1.111 if target_price > 0 else 0

        upside = round(
            (target_price - entry_price) / entry_price * 100,
            2
        ) if entry_price > 0 else 0

        downside = round(
            (entry_price - stop_loss) / entry_price * 100,
            2
        ) if entry_price > 0 else 0

        payoff = round(
            upside / downside,
            2
        ) if downside > 0 else 0

        if row["signal"] in ["BUY", "STRONG_BUY"] and risk_score >= 60:
            entry_status = "ENTRY_OK"
        elif row["signal"] in ["BUY", "STRONG_BUY"]:
            entry_status = "ENTRY_WAIT"
        else:
            entry_status = "ENTRY_BLOCK"

        return templates.TemplateResponse(
            "stock_detail.html",
            {
                "request": request,
                "stock_code": row["stock_code"],
                "stock_name": row["stock_name"],
                "committee_score": committee_score,
                "signal": row["signal"],
                "entry_status": entry_status,
                "risk_score": risk_score,
                "confidence": confidence,
                "target_price": f"{int(target_price):,}원",
                "stop_loss": f"{int(stop_loss):,}원",
                "target_price_number": int(target_price),
                "stop_loss_number": int(stop_loss),
                "smart_money": f"{int(row['smart_money_net'] or 0):,}원",
                "upside": upside,
                "downside": downside,
                "payoff": payoff
            }
        )

    finally:
        db.close()
