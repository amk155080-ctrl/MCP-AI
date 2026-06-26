from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v6/order",
    tags=["order-safe-plan-v6"]
)


@router.get("/safe-plan")
def order_safe_plan(
    capital: int = Query(..., description="총 투자금"),
    limit: int = Query(5, description="주문 계획 종목 수"),
    max_loss_percent: float = Query(5.0, description="허용 최대 포트폴리오 손실률")
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
                "message": "안전 주문표 대상 종목이 없습니다."
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
                "message": "안전 주문 가능한 후보가 없습니다."
            }

        total_weight = sum(
            item["base_weight"]
            for item in candidates
        )

        raw_orders = []

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

            raw_orders.append({
                "trade_date": item["trade_date"],
                "stock_code": item["stock_code"],
                "stock_name": item["stock_name"],
                "entry_status": item["entry_status"],
                "final_signal": item["final_signal"],
                "committee_score": item["committee_score"],
                "risk_score": item["risk_score"],
                "estimated_entry_price": estimated_entry_price,
                "target_price": item["target_price"],
                "stop_loss": item["stop_loss"],
                "raw_weight_percent": round(weight_percent, 2),
                "raw_quantity": quantity,
                "raw_order_amount": real_order_amount,
                "loss_per_share": round(loss_per_share, 0),
                "raw_expected_loss_amount": expected_loss_amount
            })

        raw_total_expected_loss = sum(
            item["raw_expected_loss_amount"]
            for item in raw_orders
        )

        allowed_loss_amount = int(
            capital * max_loss_percent / 100
        )

        if raw_total_expected_loss > 0:
            reduce_ratio = min(
                allowed_loss_amount / raw_total_expected_loss,
                1.0
            )
        else:
            reduce_ratio = 1.0

        safe_orders = []

        for item in raw_orders:
            safe_quantity = int(
                item["raw_quantity"] * reduce_ratio
            )

            safe_order_amount = int(
                safe_quantity * item["estimated_entry_price"]
            )

            safe_expected_loss_amount = int(
                item["loss_per_share"] * safe_quantity
            )

            safe_weight_percent = round(
                safe_order_amount / capital * 100,
                2
            ) if capital > 0 else 0

            safe_loss_percent = round(
                safe_expected_loss_amount / capital * 100,
                2
            ) if capital > 0 else 0

            safe_orders.append({
                "trade_date": item["trade_date"],
                "stock_code": item["stock_code"],
                "stock_name": item["stock_name"],
                "entry_status": item["entry_status"],
                "final_signal": item["final_signal"],
                "committee_score": item["committee_score"],
                "risk_score": item["risk_score"],
                "order_type": make_safe_order_type(item["entry_status"]),
                "estimated_entry_price": item["estimated_entry_price"],
                "quantity": safe_quantity,
                "order_amount": safe_order_amount,
                "weight_percent": safe_weight_percent,
                "target_price": item["target_price"],
                "stop_loss": item["stop_loss"],
                "expected_loss_amount": safe_expected_loss_amount,
                "loss_percent_of_total_capital": safe_loss_percent,
                "memo": make_safe_memo(
                    item["entry_status"],
                    safe_quantity,
                    reduce_ratio
                )
            })

        safe_orders = [
            item for item in safe_orders
            if item["quantity"] > 0
        ]

        safe_total_order_amount = sum(
            item["order_amount"]
            for item in safe_orders
        )

        safe_total_expected_loss = sum(
            item["expected_loss_amount"]
            for item in safe_orders
        )

        safe_portfolio_loss_percent = round(
            safe_total_expected_loss / capital * 100,
            2
        ) if capital > 0 else 0

        return {
            "found": True,
            "version": "MCP 6.6",
            "capital": capital,
            "max_loss_percent": max_loss_percent,
            "allowed_loss_amount": allowed_loss_amount,
            "raw_total_expected_loss": raw_total_expected_loss,
            "raw_portfolio_loss_percent": round(
                raw_total_expected_loss / capital * 100,
                2
            ) if capital > 0 else 0,
            "reduce_ratio": round(reduce_ratio, 4),
            "safe_total_order_amount": safe_total_order_amount,
            "cash": capital - safe_total_order_amount,
            "safe_total_expected_loss": safe_total_expected_loss,
            "safe_portfolio_loss_percent": safe_portfolio_loss_percent,
            "order_count": len(safe_orders),
            "orders": safe_orders,
            "comment": make_portfolio_comment(
                safe_portfolio_loss_percent,
                max_loss_percent
            )
        }

    finally:
        db.close()


def make_safe_order_type(entry_status: str):
    if entry_status == "ENTRY_OK":
        return "리스크 조정 분할 매수"
    elif entry_status == "ENTRY_WAIT":
        return "리스크 조정 소액 매수"
    else:
        return "주문 제외"


def make_safe_memo(
    entry_status: str,
    quantity: int,
    reduce_ratio: float
):
    if quantity <= 0:
        return "리스크 한도 초과로 주문 제외"
    if reduce_ratio < 0.5:
        return "손실 한도 초과로 주문 수량 대폭 축소"
    if entry_status == "ENTRY_WAIT":
        return "관찰 종목, 제한 수량만 매수"
    return "손실 한도 내 매수 가능"


def make_portfolio_comment(
    safe_portfolio_loss_percent: float,
    max_loss_percent: float
):
    if safe_portfolio_loss_percent <= max_loss_percent:
        return "허용 손실률 이내로 주문표 자동 축소 완료"
    return "허용 손실률 초과, 추가 비중 축소 필요"
