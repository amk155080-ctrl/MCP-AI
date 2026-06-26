from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
import json

from app.core.database import SessionLocal

router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@router.get("/dashboard")
def dashboard(
    request: Request
):
    db = SessionLocal()

    try:
        log = db.execute(text("""
            SELECT *
            FROM mcp4.execution_log
            ORDER BY id DESC
            LIMIT 1
        """)).mappings().first()

        rows = db.execute(text("""
            SELECT
                stock_code,
                stock_name,
                total_score,
                risk_score,
                confidence,
                smart_money_net
            FROM mcp4.recommendation_history
            WHERE trade_date = (
                SELECT MAX(trade_date)
                FROM mcp4.recommendation_history
            )
            ORDER BY total_score DESC
            LIMIT 5
        """)).mappings().all()

        recommendations = []

        for row in rows:
            total_score = float(row["total_score"] or 0)
            risk_score = float(row["risk_score"] or 0)
            confidence = float(row["confidence"] or 0)
            smart_money_net = int(row["smart_money_net"] or 0)

            committee_score = round(
                total_score * 0.5 +
                risk_score * 0.2 +
                confidence * 0.3,
                2
            )

            if committee_score >= 80:
                final_signal = "STRONG_BUY"
            elif committee_score >= 70:
                final_signal = "BUY"
            elif committee_score >= 60:
                final_signal = "HOLD"
            else:
                final_signal = "SELL"

            if final_signal in ["STRONG_BUY", "BUY"] and risk_score >= 60:
                entry_status = "ENTRY_OK"
            elif final_signal in ["STRONG_BUY", "BUY"]:
                entry_status = "ENTRY_WAIT"
            else:
                entry_status = "ENTRY_BLOCK"

            recommendations.append({
                "stock_code": row["stock_code"],
                "stock_name": row["stock_name"],
                "committee_score": committee_score,
                "smart_money_net": smart_money_net,
                "smart_money_net_text": f"{smart_money_net:,}원",
                "final_signal": final_signal,
                "entry_status": entry_status
            })

        stock_names = [
            item["stock_name"]
            for item in recommendations
        ]

        committee_scores = [
            item["committee_score"]
            for item in recommendations
        ]

        smart_money_values = [
            item["smart_money_net"]
            for item in recommendations
        ]

        safe_total_order_amount = int(
            log["safe_total_order_amount"] or 0
        )

        cash = int(
            log["cash"] or 0
        )

        safe_loss = float(
            log["safe_portfolio_loss_percent"] or 0
        )

        raw_loss = float(
            log["raw_portfolio_loss_percent"] or 0
        )

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "dashboard_status": "READY",
                "strategy_grade": log["strategy_grade"],
                "final_execution": log["final_execution"],
                "top_stock_name": log["top_stock_name"],
                "safe_total_order_amount": f"{safe_total_order_amount:,}원",
                "cash": f"{cash:,}원",
                "safe_portfolio_loss_percent": safe_loss,
                "raw_portfolio_loss_percent": raw_loss,
                "safe_total_order_amount_number": safe_total_order_amount,
                "cash_number": cash,
                "recommendations": recommendations,
                "stock_names": json.dumps(stock_names, ensure_ascii=False),
                "committee_scores": json.dumps(committee_scores),
                "smart_money_values": json.dumps(smart_money_values)
            }
        )

    finally:
        db.close()
