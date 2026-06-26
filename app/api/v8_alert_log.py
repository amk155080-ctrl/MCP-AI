from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v8/alert",
    tags=["alert-log-v8"]
)


@router.get("/save")
def save_alert_log(
    limit: int = Query(20),
    price_mode: str = Query("normal")
):
    db = SessionLocal()

    try:
        rows = db.execute(text("""
            SELECT
                stock_code,
                stock_name,
                target_price,
                stop_loss,
                total_score
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

        target_near_count = 0
        stop_loss_count = 0

        for row in rows:
            target_price = float(row["target_price"] or 0)
            stop_loss = float(row["stop_loss"] or 0)

            if target_price <= 0 or stop_loss <= 0:
                continue

            if price_mode == "stop":
                current_price = round(stop_loss * 0.99, 0)
            else:
                current_price = round(target_price * 0.955, 0)

            progress = round(current_price / target_price * 100, 2)

            if current_price <= stop_loss:
                stop_loss_count += 1
            elif progress >= 95:
                target_near_count += 1

        if stop_loss_count > 0:
            alert_level = "DANGER"
            action = "손절가 이탈 종목 우선 확인"
        elif target_near_count > 0:
            alert_level = "NOTICE"
            action = "목표가 근접 종목 익절 전략 점검"
        else:
            alert_level = "NORMAL"
            action = "특이 알림 없음"

        message = (
            f"상태={alert_level}, "
            f"목표근접={target_near_count}, "
            f"손절경고={stop_loss_count}, "
            f"조치={action}"
        )

        result = db.execute(text("""
            INSERT INTO mcp4.alert_log (
                version,
                alert_level,
                target_near_count,
                stop_loss_count,
                action,
                message
            )
            VALUES (
                'MCP 8.5',
                :alert_level,
                :target_near_count,
                :stop_loss_count,
                :action,
                :message
            )
            RETURNING id
        """), {
            "alert_level": alert_level,
            "target_near_count": target_near_count,
            "stop_loss_count": stop_loss_count,
            "action": action,
            "message": message
        })

        log_id = result.scalar()
        db.commit()

        return {
            "found": True,
            "saved": True,
            "version": "MCP 8.5",
            "log_id": log_id,
            "price_mode": price_mode,
            "alert_level": alert_level,
            "target_near_count": target_near_count,
            "stop_loss_count": stop_loss_count,
            "action": action,
            "message": message
        }

    finally:
        db.close()

@router.get("/logs")
def alert_logs(
    limit: int = Query(10)
):
    db = SessionLocal()

    try:

        rows = db.execute(text("""
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
            LIMIT :limit
        """), {
            "limit": limit
        }).mappings().all()

        items = [dict(r) for r in rows]

        latest = items[0] if items else None

        return {
            "found": True,
            "version": "MCP 8.6",
            "count": len(items),
            "latest": latest,
            "items": items,
            "comment": "알림 로그 조회 완료"
        }

    finally:
        db.close()


@router.get("/stats")
def alert_stats():
    db = SessionLocal()

    try:
        total = db.execute(text("""
            SELECT COUNT(*) AS count
            FROM mcp4.alert_log
        """)).mappings().first()

        by_level = db.execute(text("""
            SELECT
                alert_level,
                COUNT(*) AS count
            FROM mcp4.alert_log
            GROUP BY alert_level
            ORDER BY count DESC
        """)).mappings().all()

        recent = db.execute(text("""
            SELECT
                id,
                created_at,
                alert_level,
                target_near_count,
                stop_loss_count,
                action
            FROM mcp4.alert_log
            ORDER BY id DESC
            LIMIT 30
        """)).mappings().all()

        level_counts = {
            "NORMAL": 0,
            "NOTICE": 0,
            "DANGER": 0
        }

        for row in by_level:
            level_counts[row["alert_level"]] = int(row["count"] or 0)

        recent_items = []

        for row in recent:
            recent_items.append({
                "id": row["id"],
                "created_at": str(row["created_at"]),
                "alert_level": row["alert_level"],
                "target_near_count": int(row["target_near_count"] or 0),
                "stop_loss_count": int(row["stop_loss_count"] or 0),
                "action": row["action"]
            })

        total_count = int(total["count"] or 0)

        danger_ratio = round(
            level_counts["DANGER"] / total_count * 100,
            2
        ) if total_count > 0 else 0

        notice_ratio = round(
            level_counts["NOTICE"] / total_count * 100,
            2
        ) if total_count > 0 else 0

        normal_ratio = round(
            level_counts["NORMAL"] / total_count * 100,
            2
        ) if total_count > 0 else 0

        if level_counts["DANGER"] > 0:
            risk_trend = "HIGH_RISK_HISTORY"
            comment = "최근 알림 이력에 손절 경고가 포함되어 있습니다."
        elif level_counts["NOTICE"] > 0:
            risk_trend = "NOTICE_DOMINANT"
            comment = "최근 알림 이력은 목표가 근접 알림 중심입니다."
        else:
            risk_trend = "NORMAL"
            comment = "최근 알림 이력상 특이 위험 신호가 없습니다."

        return {
            "found": True,
            "version": "MCP 8.7",
            "total_logs": total_count,
            "level_counts": level_counts,
            "ratios": {
                "normal_percent": normal_ratio,
                "notice_percent": notice_ratio,
                "danger_percent": danger_ratio
            },
            "risk_trend": risk_trend,
            "recent_count": len(recent_items),
            "recent_items": recent_items,
            "comment": comment
        }

    finally:
        db.close()
