from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v6/order",
    tags=["order-plan-v6"]
)


@router.get("/plan")
def order_plan(
    capital: int = Query(..., description="총 투자금"),
    limit: int = Query(5, description="주문 계획 종목 수")
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
                "message": "주문 계획 대상 종목이 없습니다."
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
                    "total_score": total_score,
                    "risk_score": risk_score,
                    "confidence": confidence,
                    "target_price": target_price,
                    "stop_loss": stop_loss,
                    "smart_money_net": int(row["smart_money_net"] or 0),
                    "base_weight": base_weight
                })

        if not candidates:
            return {
                "found": False,
                "message": "주문 가능 종목이 없습니다."
            }

        total_weight = sum(
            item["base_weight"]
            for item in candidates
        )

        order_plan_items = []

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

            order_amount = int(capital * weight_percent / 100)

            # 현재가 데이터가 아직 없으므로 target_price 기준 90%를 임시 기준가로 사용
            estimated_entry_price = round(item["target_price"] * 0.9, 0)

            quantity = int(
                order_amount / estimated_entry_price
            ) if estimated_entry_price > 0 else 0

            real_order_amount = int(
                quantity * estimated_entry_price
            )

            order_plan_items.append({
                "trade_date": item["trade_date"],
                "stock_code": item["stock_code"],
                "stock_name": item["stock_name"],
                "entry_status": item["entry_status"],
                "final_signal": item["final_signal"],
                "committee_score": item["committee_score"],
                "risk_score": item["risk_score"],
                "order_type": make_order_type(item["entry_status"]),
                "recommended_weight_percent": round(weight_percent, 2),
                "planned_amount": order_amount,
                "estimated_entry_price": estimated_entry_price,
                "quantity": quantity,
                "real_order_amount": real_order_amount,
                "target_price": item["target_price"],
                "stop_loss": item["stop_loss"],
                "risk_per_share": round(
                    estimated_entry_price - item["stop_loss"],
                    0
                ),
                "expected_upside_percent": round(
                    (
                        (item["target_price"] - estimated_entry_price)
                        / estimated_entry_price
                    ) * 100,
                    2
                ) if estimated_entry_price > 0 else 0,
                "stop_loss_percent": round(
                    (
                        (estimated_entry_price - item["stop_loss"])
                        / estimated_entry_price
                    ) * 100,
                    2
                ) if estimated_entry_price > 0 else 0,
                "memo": make_order_memo(
                    item["entry_status"],
                    item["risk_score"]
                )
            })

        used_capital = sum(
            item["real_order_amount"]
            for item in order_plan_items
        )

        return {
            "found": True,
            "version": "MCP 6.4",
            "capital": capital,
            "used_capital": used_capital,
            "cash": capital - used_capital,
            "order_count": len(order_plan_items),
            "orders": order_plan_items,
            "comment": "매수 주문표 생성 완료"
        }

    finally:
        db.close()


def make_order_type(entry_status: str):
    if entry_status == "ENTRY_OK":
        return "분할 지정가 매수"
    elif entry_status == "ENTRY_WAIT":
        return "소액 관찰 매수"
    else:
        return "주문 보류"


def make_order_memo(entry_status: str, risk_score: float):
    if entry_status == "ENTRY_OK" and risk_score >= 70:
        return "리스크 양호, 계획 비중 매수 가능"
    elif entry_status == "ENTRY_OK":
        return "진입 가능, 분할 매수 권장"
    elif entry_status == "ENTRY_WAIT":
        return "리스크 점수 부족, 소액 관찰 권장"
    else:
        return "조건 미충족"
