from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v6/order",
    tags=["order-risk-check-v6"]
)


@router.get("/risk-check")
def order_risk_check(
    capital: int = Query(..., description="총 투자금"),
    limit: int = Query(5, description="리스크 점검 종목 수")
):
    db = SessionLocal()

    try:
        rows = db.execute(text("""
            SELECT
                trade_date,
                stock_code,
                stock_name,
                total_score,
                risk_score,
                signal,
                confidence,
                target_price,
                stop_loss,
                smart_money_net
            FROM mcp4.recommendation_history
            WHERE trade_date = (
                SELECT MAX(trade_date)
                FROM mcp4.recommendation_history
            )
            ORDER BY total_score DESC
            LIMIT :limit
        """), {
            "limit": limit
        }).mappings().all()

        if not rows:
            return {
                "found": False,
                "message": "리스크 점검 대상 종목이 없습니다."
            }

        candidates = []

        for row in rows:
            total_score = float(row["total_score"] or 0)
            risk_score = float(row["risk_score"] or 0)
            confidence = float(row["confidence"] or 0)
            target_price = float(row["target_price"] or 0)
            stop_loss = float(row["stop_loss"] or 0)

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

            if (
                final_signal in ["STRONG_BUY", "BUY"]
                and committee_score >= 70
                and confidence >= 70
                and target_price > 0
                and stop_loss > 0
            ):
                entry_status = "ENTRY_OK" if risk_score >= 60 else "ENTRY_WAIT"
            else:
                entry_status = "ENTRY_BLOCK"

            if entry_status in ["ENTRY_OK", "ENTRY_WAIT"]:
                base_weight = committee_score

                if entry_status == "ENTRY_WAIT":
                    base_weight *= 0.5

                if risk_score < 60:
                    base_weight *= 0.8

                candidates.append({
                    "trade_date": str(row["trade_date"]),
                    "stock_code": row["stock_code"],
                    "stock_name": row["stock_name"],
                    "committee_score": committee_score,
                    "final_signal": final_signal,
                    "entry_status": entry_status,
                    "risk_score": risk_score,
                    "target_price": target_price,
                    "stop_loss": stop_loss,
                    "base_weight": base_weight
                })

        if not candidates:
            return {
                "found": False,
                "message": "리스크 점검 가능한 주문 후보가 없습니다."
            }

        total_weight = sum(
            item["base_weight"]
            for item in candidates
        )

        risk_items = []

        for item in candidates:
            weight_percent = (
                item["base_weight"] / total_weight * 100
                if total_weight > 0
                else 0
            )

            if item["entry_status"] == "ENTRY_OK":
                max_weight = 35.0
            else:
                max_weight = 15.0

            weight_percent = min(weight_percent, max_weight)

            planned_amount = int(
                capital * weight_percent / 100
            )

            estimated_entry_price = round(
                item["target_price"] * 0.9,
                0
            )

            quantity = int(
                planned_amount / estimated_entry_price
            ) if estimated_entry_price > 0 else 0

            real_order_amount = int(
                quantity * estimated_entry_price
            )

            loss_per_share = max(
                estimated_entry_price - item["stop_loss"],
                0
            )

            expected_loss_amount = int(
                loss_per_share * quantity
            )

            loss_rate_percent = round(
                expected_loss_amount / capital * 100,
                2
            ) if capital > 0 else 0

            position_loss_percent = round(
                expected_loss_amount / real_order_amount * 100,
                2
            ) if real_order_amount > 0 else 0

            risk_items.append({
                "stock_code": item["stock_code"],
                "stock_name": item["stock_name"],
                "entry_status": item["entry_status"],
                "committee_score": item["committee_score"],
                "risk_score": item["risk_score"],
                "estimated_entry_price": estimated_entry_price,
                "stop_loss": item["stop_loss"],
                "quantity": quantity,
                "real_order_amount": real_order_amount,
                "loss_per_share": round(loss_per_share, 0),
                "expected_loss_amount": expected_loss_amount,
                "loss_rate_percent_of_total_capital": loss_rate_percent,
                "loss_rate_percent_of_position": position_loss_percent,
                "risk_level": make_risk_level(
                    loss_rate_percent,
                    position_loss_percent
                ),
                "memo": make_risk_memo(
                    loss_rate_percent,
                    position_loss_percent
                )
            })

        total_order_amount = sum(
            item["real_order_amount"]
            for item in risk_items
        )

        total_expected_loss = sum(
            item["expected_loss_amount"]
            for item in risk_items
        )

        portfolio_loss_percent = round(
            total_expected_loss / capital * 100,
            2
        ) if capital > 0 else 0

        if portfolio_loss_percent <= 3:
            portfolio_risk_level = "LOW"
            portfolio_comment = "포트폴리오 전체 리스크 양호"
        elif portfolio_loss_percent <= 5:
            portfolio_risk_level = "MEDIUM"
            portfolio_comment = "포트폴리오 리스크 보통, 분할 진입 권장"
        else:
            portfolio_risk_level = "HIGH"
            portfolio_comment = "포트폴리오 손실 위험 과다, 비중 축소 필요"

        return {
            "found": True,
            "version": "MCP 6.5",
            "capital": capital,
            "total_order_amount": total_order_amount,
            "cash": capital - total_order_amount,
            "total_expected_loss": total_expected_loss,
            "portfolio_loss_percent": portfolio_loss_percent,
            "portfolio_risk_level": portfolio_risk_level,
            "items": risk_items,
            "comment": portfolio_comment
        }

    finally:
        db.close()


def make_risk_level(
    loss_rate_percent: float,
    position_loss_percent: float
):
    if loss_rate_percent <= 0.7 and position_loss_percent <= 10:
        return "LOW"
    elif loss_rate_percent <= 1.2 and position_loss_percent <= 15:
        return "MEDIUM"
    else:
        return "HIGH"


def make_risk_memo(
    loss_rate_percent: float,
    position_loss_percent: float
):
    if loss_rate_percent <= 0.7 and position_loss_percent <= 10:
        return "손실 위험 낮음"
    elif loss_rate_percent <= 1.2 and position_loss_percent <= 15:
        return "손실 위험 보통"
    else:
        return "손실 위험 높음, 비중 축소 검토"
