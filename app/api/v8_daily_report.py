from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v8/report",
    tags=["daily-report-v8"]
)


@router.get("/daily")
def daily_report():
    db = SessionLocal()

    try:
        execution = db.execute(text("""
            SELECT
                id,
                trade_date,
                final_execution,
                strategy_grade,
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

        alert = db.execute(text("""
            SELECT
                id,
                created_at,
                version,
                alert_level,
                target_near_count,
                stop_loss_count,
                action,
                message
            FROM mcp4.alert_log
            ORDER BY id DESC
            LIMIT 1
        """)).mappings().first()

        if not execution:
            return {
                "found": False,
                "message": "실행 로그가 없습니다. 먼저 /api/v6/execution/save 를 실행하세요."
            }

        if not alert:
            alert_level = "NORMAL"
            target_near_count = 0
            stop_loss_count = 0
            alert_action = "알림 로그 없음"
            alert_message = "저장된 알림 로그가 없습니다."
        else:
            alert_level = alert["alert_level"]
            target_near_count = int(alert["target_near_count"] or 0)
            stop_loss_count = int(alert["stop_loss_count"] or 0)
            alert_action = alert["action"]
            alert_message = alert["message"]

        final_execution = execution["final_execution"]
        strategy_grade = execution["strategy_grade"]
        top_stock_name = execution["top_stock_name"]

        safe_order_amount = int(execution["safe_total_order_amount"] or 0)
        cash = int(execution["cash"] or 0)
        safe_loss = float(execution["safe_portfolio_loss_percent"] or 0)
        raw_loss = float(execution["raw_portfolio_loss_percent"] or 0)
        reduce_ratio = float(execution["reduce_ratio"] or 0)

        report_title = "MCP 일일 투자 리포트"

        headline = make_headline(
            final_execution,
            strategy_grade,
            alert_level
        )

        summary = (
            f"전략 등급은 {strategy_grade}이며, "
            f"최종 실행 판단은 {final_execution}입니다. "
            f"최우선 종목은 {top_stock_name}입니다. "
            f"원래 예상 손실률은 {raw_loss}%였고, "
            f"리스크 조정 후 예상 손실률은 {safe_loss}%입니다."
        )

        risk_summary = (
            f"안전 주문금액은 {safe_order_amount:,}원, "
            f"현금 보유액은 {cash:,}원입니다. "
            f"주문 비중은 기존 대비 약 {round(reduce_ratio * 100, 1)}% 수준으로 축소되었습니다."
        )

        alert_summary = (
            f"현재 알림 상태는 {alert_level}입니다. "
            f"목표가 근접 종목은 {target_near_count}개, "
            f"손절 경고 종목은 {stop_loss_count}개입니다."
        )

        kakao_message = make_kakao_message(
            report_title,
            strategy_grade,
            final_execution,
            top_stock_name,
            safe_order_amount,
            cash,
            safe_loss,
            raw_loss,
            alert_level,
            target_near_count,
            stop_loss_count,
            alert_action
        )

        return {
            "found": True,
            "version": "MCP 8.8",
            "title": report_title,
            "headline": headline,
            "trade_date": str(execution["trade_date"]),
            "execution": {
                "log_id": execution["id"],
                "final_execution": final_execution,
                "strategy_grade": strategy_grade,
                "top_stock_code": execution["top_stock_code"],
                "top_stock_name": top_stock_name,
                "safe_total_order_amount": safe_order_amount,
                "cash": cash,
                "safe_total_expected_loss": int(execution["safe_total_expected_loss"] or 0),
                "safe_portfolio_loss_percent": safe_loss,
                "raw_portfolio_loss_percent": raw_loss,
                "reduce_ratio": reduce_ratio,
                "comment": execution["comment"],
                "created_at": str(execution["created_at"])
            },
            "alert": {
                "alert_level": alert_level,
                "target_near_count": target_near_count,
                "stop_loss_count": stop_loss_count,
                "action": alert_action,
                "message": alert_message
            },
            "summary": summary,
            "risk_summary": risk_summary,
            "alert_summary": alert_summary,
            "kakao_message": kakao_message,
            "comment": "일일 투자 리포트 생성 완료"
        }

    finally:
        db.close()


def make_headline(
    final_execution: str,
    strategy_grade: str,
    alert_level: str
):
    if final_execution == "SAFE_EXECUTE" and alert_level != "DANGER":
        return f"전략은 {strategy_grade}등급이며, 리스크 한도 내 실행 가능한 상태입니다."

    if alert_level == "DANGER":
        return f"전략은 {strategy_grade}등급이나, 손절 경고가 있어 즉시 점검이 필요합니다."

    if final_execution == "PARTIAL_EXECUTE":
        return f"전략은 {strategy_grade}등급이며, 일부 분할 실행이 적합합니다."

    return f"전략은 {strategy_grade}등급이며, 현재는 관망 또는 추가 확인이 필요합니다."


def make_kakao_message(
    title: str,
    strategy_grade: str,
    final_execution: str,
    top_stock_name: str,
    safe_order_amount: int,
    cash: int,
    safe_loss: float,
    raw_loss: float,
    alert_level: str,
    target_near_count: int,
    stop_loss_count: int,
    alert_action: str
):
    return f"""
📊 {title}

전략등급: {strategy_grade}
실행판단: {final_execution}
TOP PICK: {top_stock_name}

안전 주문금액: {safe_order_amount:,}원
현금: {cash:,}원

원래 손실률: {raw_loss}%
안전 손실률: {safe_loss}%

알림상태: {alert_level}
목표가 근접: {target_near_count}개
손절 경고: {stop_loss_count}개

조치:
{alert_action}
""".strip()
