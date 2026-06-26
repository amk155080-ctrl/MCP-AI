from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v7/dashboard",
    tags=["dashboard-summary-text-v7"]
)


@router.get("/summary-text")
def dashboard_summary_text(
    capital: int = Query(...),
    limit: int = Query(5),
    max_loss_percent: float = Query(5.0)
):
    db = SessionLocal()

    try:
        latest_log = db.execute(text("""
            SELECT
                id,
                trade_date,
                final_execution,
                strategy_grade,
                candidate_count,
                entry_ok_count,
                entry_wait_count,
                top_stock_code,
                top_stock_name,
                safe_total_order_amount,
                cash,
                safe_total_expected_loss,
                safe_portfolio_loss_percent,
                raw_portfolio_loss_percent,
                reduce_ratio,
                comment,
                created_at
            FROM mcp4.execution_log
            ORDER BY id DESC
            LIMIT 1
        """)).mappings().first()

        if not latest_log:
            return {
                "found": False,
                "message": "실행 로그가 없습니다. 먼저 /api/v6/execution/save 를 실행하세요."
            }

        final_execution = latest_log["final_execution"]
        strategy_grade = latest_log["strategy_grade"]
        top_stock_name = latest_log["top_stock_name"]

        safe_order_amount = int(latest_log["safe_total_order_amount"] or 0)
        cash = int(latest_log["cash"] or 0)
        safe_loss = float(latest_log["safe_portfolio_loss_percent"] or 0)
        raw_loss = float(latest_log["raw_portfolio_loss_percent"] or 0)
        reduce_ratio = float(latest_log["reduce_ratio"] or 0)

        entry_ok_count = int(latest_log["entry_ok_count"] or 0)
        entry_wait_count = int(latest_log["entry_wait_count"] or 0)

        dashboard_status = make_dashboard_status(final_execution)

        headline = make_headline(
            final_execution,
            strategy_grade,
            top_stock_name
        )

        summary = make_summary(
            final_execution,
            strategy_grade,
            top_stock_name,
            safe_order_amount,
            cash,
            safe_loss,
            raw_loss,
            reduce_ratio,
            entry_ok_count,
            entry_wait_count
        )

        action_guide = make_action_guide(
            final_execution,
            safe_loss,
            max_loss_percent
        )

        risk_message = make_risk_message(
            safe_loss,
            raw_loss,
            reduce_ratio
        )

        return {
            "found": True,
            "version": "MCP 7.1",
            "dashboard_status": dashboard_status,
            "headline": headline,
            "summary": summary,
            "action_guide": action_guide,
            "risk_message": risk_message,
            "data": {
                "log_id": latest_log["id"],
                "trade_date": str(latest_log["trade_date"]),
                "final_execution": final_execution,
                "strategy_grade": strategy_grade,
                "top_stock_name": top_stock_name,
                "safe_total_order_amount": safe_order_amount,
                "cash": cash,
                "safe_portfolio_loss_percent": safe_loss,
                "raw_portfolio_loss_percent": raw_loss,
                "reduce_ratio": reduce_ratio,
                "entry_ok_count": entry_ok_count,
                "entry_wait_count": entry_wait_count,
                "created_at": str(latest_log["created_at"])
            },
            "comment": "대시보드 요약 문장 생성 완료"
        }

    finally:
        db.close()


def make_dashboard_status(final_execution: str):
    if final_execution == "SAFE_EXECUTE":
        return "READY"
    elif final_execution == "PARTIAL_EXECUTE":
        return "CAUTION"
    elif final_execution == "DO_NOT_EXECUTE":
        return "WAIT"
    return "UNKNOWN"


def make_headline(
    final_execution: str,
    strategy_grade: str,
    top_stock_name: str
):
    if final_execution == "SAFE_EXECUTE":
        return f"현재 전략은 {strategy_grade}등급이며, 리스크 조정 후 실행 가능한 상태입니다."
    elif final_execution == "PARTIAL_EXECUTE":
        return f"현재 전략은 {strategy_grade}등급이나, 일부 종목만 분할 진입이 적합합니다."
    elif final_execution == "DO_NOT_EXECUTE":
        return f"현재 전략은 {strategy_grade}등급이나, 리스크가 높아 관망이 우선입니다."
    return "현재 실행 상태를 판단할 수 없습니다."


def make_summary(
    final_execution: str,
    strategy_grade: str,
    top_stock_name: str,
    safe_order_amount: int,
    cash: int,
    safe_loss: float,
    raw_loss: float,
    reduce_ratio: float,
    entry_ok_count: int,
    entry_wait_count: int
):
    safe_order_amount_text = f"{safe_order_amount:,}원"
    cash_text = f"{cash:,}원"

    if final_execution == "SAFE_EXECUTE":
        return (
            f"최종 판단은 SAFE_EXECUTE입니다. "
            f"전략 등급은 {strategy_grade}이며, 최우선 종목은 {top_stock_name}입니다. "
            f"진입 가능 종목은 {entry_ok_count}개, 관찰 진입 종목은 {entry_wait_count}개입니다. "
            f"원래 포트폴리오 손실률은 {raw_loss}%였지만, 리스크 조정 후 예상 손실률은 {safe_loss}%로 낮아졌습니다. "
            f"총 주문 예정 금액은 {safe_order_amount_text}, 현금 보유액은 {cash_text}입니다."
        )

    if final_execution == "PARTIAL_EXECUTE":
        return (
            f"최종 판단은 PARTIAL_EXECUTE입니다. "
            f"전략 등급은 {strategy_grade}이며, 최우선 종목은 {top_stock_name}입니다. "
            f"다만 리스크가 남아 있어 전체 진입보다는 일부 종목 중심의 분할 진입이 적합합니다. "
            f"현재 안전 주문 예정 금액은 {safe_order_amount_text}, 예상 손실률은 {safe_loss}%입니다."
        )

    if final_execution == "DO_NOT_EXECUTE":
        return (
            f"최종 판단은 DO_NOT_EXECUTE입니다. "
            f"전략 등급은 {strategy_grade}이나, 현재 손실 위험이 높아 신규 진입보다는 관망이 적합합니다. "
            f"원래 예상 손실률은 {raw_loss}%이며, 리스크 조정 후에도 충분히 낮아지지 않았습니다."
        )

    return "요약 문장을 생성할 수 없습니다."


def make_action_guide(
    final_execution: str,
    safe_loss: float,
    max_loss_percent: float
):
    if final_execution == "SAFE_EXECUTE" and safe_loss <= max_loss_percent:
        return "안전 주문표 기준으로만 분할 매수를 검토할 수 있습니다."

    if final_execution == "PARTIAL_EXECUTE":
        return "ENTRY_OK 종목 위주로 소액 분할 진입하고, ENTRY_WAIT 종목은 관찰이 우선입니다."

    if final_execution == "DO_NOT_EXECUTE":
        return "현재는 신규 진입을 보류하고 다음 신호를 기다리는 것이 좋습니다."

    return "추가 확인이 필요합니다."


def make_risk_message(
    safe_loss: float,
    raw_loss: float,
    reduce_ratio: float
):
    if raw_loss > safe_loss:
        return (
            f"리스크 조정으로 예상 손실률이 {raw_loss}%에서 {safe_loss}%로 낮아졌습니다. "
            f"주문 비중은 기존 대비 약 {round(reduce_ratio * 100, 1)}% 수준으로 축소되었습니다."
        )

    return "현재 리스크 조정이 크게 필요하지 않은 상태입니다."
