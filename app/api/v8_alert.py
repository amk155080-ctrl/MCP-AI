from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v8/alert",
    tags=["alert-v8"]
)


def get_current_price(target_price: float, stop_loss: float, price_mode: str):
    if price_mode == "stop":
        return round(stop_loss * 0.99, 0)

    return round(target_price * 0.955, 0)


def load_latest_recommendations(db, limit: int):
    return db.execute(text("""
        SELECT
            stock_code,
            stock_name,
            target_price,
            stop_loss,
            total_score,
            risk_score,
            confidence
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


def build_alert_summary(db, limit: int, price_mode: str):
    rows = load_latest_recommendations(db, limit)

    target_near_items = []
    stop_loss_items = []
    normal_items = []

    for row in rows:
        target_price = float(row["target_price"] or 0)
        stop_loss = float(row["stop_loss"] or 0)

        if target_price <= 0 or stop_loss <= 0:
            continue

        current_price = get_current_price(
            target_price,
            stop_loss,
            price_mode
        )

        target_progress_percent = round(
            current_price / target_price * 100,
            2
        )

        stop_gap_percent = round(
            (current_price - stop_loss) / stop_loss * 100,
            2
        )

        item = {
            "stock_code": row["stock_code"],
            "stock_name": row["stock_name"],
            "current_price": current_price,
            "target_price": target_price,
            "stop_loss": stop_loss,
            "target_progress_percent": target_progress_percent,
            "stop_gap_percent": stop_gap_percent
        }

        if current_price <= stop_loss:
            item["alert"] = "STOP_LOSS_ALERT"
            item["message"] = "손절가 이탈 경고"
            stop_loss_items.append(item)

        elif target_progress_percent >= 95:
            item["alert"] = "TARGET_NEAR"
            item["message"] = "목표가 근접"
            target_near_items.append(item)

        else:
            item["alert"] = "NORMAL"
            item["message"] = "정상 보유 구간"
            normal_items.append(item)

    if stop_loss_items:
        alert_level = "DANGER"
        action = "손절가 이탈 종목 우선 확인"
    elif target_near_items:
        alert_level = "NOTICE"
        action = "목표가 근접 종목 익절 전략 점검"
    else:
        alert_level = "NORMAL"
        action = "특이 알림 없음"

    return {
        "alert_level": alert_level,
        "target_near_items": target_near_items,
        "stop_loss_items": stop_loss_items,
        "normal_items": normal_items,
        "action": action
    }


@router.get("/summary")
def alert_summary(
    limit: int = Query(20),
    price_mode: str = Query("normal")
):
    db = SessionLocal()

    try:
        summary = build_alert_summary(db, limit, price_mode)

        return {
            "found": True,
            "version": "MCP 8.3",
            "price_mode": price_mode,
            "alert_level": summary["alert_level"],
            "target_near_count": len(summary["target_near_items"]),
            "stop_loss_count": len(summary["stop_loss_items"]),
            "normal_count": len(summary["normal_items"]),
            "target_near_items": summary["target_near_items"],
            "stop_loss_items": summary["stop_loss_items"],
            "normal_items": summary["normal_items"],
            "action": summary["action"],
            "comment": "통합 알림 요약 완료"
        }

    finally:
        db.close()


@router.get("/target-near")
def target_near_alert(
    limit: int = Query(20),
    price_mode: str = Query("normal")
):
    db = SessionLocal()

    try:
        summary = build_alert_summary(db, limit, price_mode)

        return {
            "found": True,
            "version": "MCP 8.1",
            "price_mode": price_mode,
            "alert_count": len(summary["target_near_items"]),
            "items": summary["target_near_items"],
            "comment": "목표가 근접 종목 조회 완료"
        }

    finally:
        db.close()


@router.get("/stop-loss")
def stop_loss_alert(
    limit: int = Query(20),
    price_mode: str = Query("normal")
):
    db = SessionLocal()

    try:
        summary = build_alert_summary(db, limit, price_mode)

        return {
            "found": True,
            "version": "MCP 8.2",
            "price_mode": price_mode,
            "alert_count": len(summary["stop_loss_items"]),
            "items": summary["stop_loss_items"],
            "comment": "손절가 경고 종목 조회 완료"
        }

    finally:
        db.close()


@router.get("/kakao")
def alert_kakao(
    limit: int = Query(20),
    price_mode: str = Query("normal")
):
    db = SessionLocal()

    try:
        summary = build_alert_summary(db, limit, price_mode)

        alert_level = summary["alert_level"]
        target_near_items = summary["target_near_items"]
        stop_loss_items = summary["stop_loss_items"]
        action = summary["action"]

        lines = []

        lines.append("🚨 MCP 알림 요약")
        lines.append("")
        lines.append(f"상태: {alert_level}")
        lines.append(f"목표가 근접: {len(target_near_items)}개")
        lines.append(f"손절 경고: {len(stop_loss_items)}개")
        lines.append("")

        if stop_loss_items:
            lines.append("⚠️ 손절 경고 종목")
            for idx, item in enumerate(stop_loss_items[:5], start=1):
                lines.append(
                    f"{idx}. {item['stock_name']} "
                    f"- 현재가 {int(item['current_price']):,}원 / "
                    f"손절가 {int(item['stop_loss']):,}원"
                )
            lines.append("")

        if target_near_items:
            lines.append("🎯 목표가 근접 종목")
            for idx, item in enumerate(target_near_items[:5], start=1):
                lines.append(
                    f"{idx}. {item['stock_name']} "
                    f"- 목표가 {item['target_progress_percent']}% 도달"
                )
            lines.append("")

        lines.append("조치:")
        lines.append(action)

        message = "\n".join(lines)

        return {
            "found": True,
            "version": "MCP 8.4",
            "price_mode": price_mode,
            "alert_level": alert_level,
            "message": message,
            "target_near_count": len(target_near_items),
            "stop_loss_count": len(stop_loss_items),
            "comment": "카카오톡 알림 문구 생성 완료"
        }

    finally:
        db.close()
