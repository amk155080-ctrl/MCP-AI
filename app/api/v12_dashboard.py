from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v12",
    tags=["MCP 12.10 Dashboard"]
)


@router.get("/dashboard")
def dashboard():
    db = SessionLocal()

    try:
        config = db.execute(
            text("""
                SELECT *
                FROM mcp4.auto_trading_config
                ORDER BY id DESC
                LIMIT 1
            """)
        ).mappings().first()

        positions = db.execute(
            text("""
                SELECT *
                FROM mcp4.portfolio_position
                ORDER BY id ASC
            """)
        ).mappings().all()

        order_status = db.execute(
            text("""
                SELECT status, COUNT(*) AS count
                FROM mcp4.order_queue
                GROUP BY status
                ORDER BY status
            """)
        ).mappings().all()

        recent_orders = db.execute(
            text("""
                SELECT *
                FROM mcp4.order_queue
                ORDER BY id DESC
                LIMIT 10
            """)
        ).mappings().all()

        recent_logs = db.execute(
            text("""
                SELECT *
                FROM mcp4.auto_trading_log
                ORDER BY id DESC
                LIMIT 10
            """)
        ).mappings().all()

        return {
            "found": True,
            "version": "MCP 12.10",
            "auto_trading_enabled": bool(config["enabled"]) if config else False,
            "auto_order_enabled": bool(config["auto_order_enabled"]) if config else False,
            "position_count": len(positions),
            "positions": [dict(x) for x in positions],
            "order_status": [dict(x) for x in order_status],
            "recent_orders": [dict(x) for x in recent_orders],
            "recent_logs": [dict(x) for x in recent_logs],
            "message": "운영 대시보드 조회 완료"
        }

    finally:
        db.close()


@router.get("/dashboard/html", response_class=HTMLResponse)
def dashboard_html():
    data = dashboard()

    auto_trading = "ON" if data["auto_trading_enabled"] else "OFF"
    auto_order = "ON" if data["auto_order_enabled"] else "OFF"

    position_rows = ""
    for p in data["positions"]:
        position_rows += f"""
        <tr>
            <td>{p.get("stock_code", "-")}</td>
            <td>{p.get("stock_name", "-")}</td>
            <td>{p.get("quantity", "-")}</td>
            <td>{p.get("buy_price", "-")}</td>
            <td>{p.get("target_price", "-")}</td>
            <td>{p.get("stop_price", "-")}</td>
        </tr>
        """

    order_status_rows = ""
    for o in data["order_status"]:
        order_status_rows += f"""
        <tr>
            <td>{o.get("status", "-")}</td>
            <td>{o.get("count", 0)}</td>
        </tr>
        """

    recent_order_rows = ""
    for o in data["recent_orders"]:
        recent_order_rows += f"""
        <tr>
            <td>{o.get("id", "-")}</td>
            <td>{o.get("stock_name", "-")}</td>
            <td>{o.get("action", "-")}</td>
            <td>{o.get("quantity", "-")}</td>
            <td>{o.get("current_price", "-")}</td>
            <td>{o.get("status", "-")}</td>
        </tr>
        """

    log_rows = ""
    for log in data["recent_logs"]:
        log_rows += f"""
        <tr>
            <td>{log.get("id", "-")}</td>
            <td>{log.get("event_type", "-")}</td>
            <td>{log.get("message", "-")}</td>
            <td>{log.get("created_at", "-")}</td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>MCP 12.10 운영 대시보드</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f4f6f9;
            margin: 0;
            padding: 30px;
        }}
        .container {{
            max-width: 1200px;
            margin: auto;
        }}
        .card {{
            background: white;
            border-radius: 14px;
            padding: 22px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        h1 {{
            color: #1f4e79;
        }}
        h2 {{
            margin-top: 0;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }}
        .stat {{
            background: #f8fafc;
            border-radius: 12px;
            padding: 18px;
            border: 1px solid #e5e7eb;
        }}
        .label {{
            color: #667085;
            font-size: 14px;
        }}
        .value {{
            font-size: 26px;
            font-weight: bold;
            margin-top: 8px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }}
        th {{
            background: #f1f5f9;
        }}
        .on {{
            color: #0a7f35;
            font-weight: bold;
        }}
        .off {{
            color: #b42318;
            font-weight: bold;
        }}
    </style>
</head>
<body>
<div class="container">

    <div class="card">
        <h1>📊 MCP 12.10 운영 대시보드</h1>
        <p>자동매매 운영 상태를 한눈에 확인하는 화면입니다.</p>
    </div>

    <div class="grid">
        <div class="stat">
            <div class="label">자동매매</div>
            <div class="value {'on' if data["auto_trading_enabled"] else 'off'}">{auto_trading}</div>
        </div>
        <div class="stat">
            <div class="label">자동 실주문</div>
            <div class="value {'on' if data["auto_order_enabled"] else 'off'}">{auto_order}</div>
        </div>
        <div class="stat">
            <div class="label">보유 포지션</div>
            <div class="value">{data["position_count"]}개</div>
        </div>
    </div>

    <div class="card">
        <h2>보유 종목</h2>
        <table>
            <tr>
                <th>종목코드</th>
                <th>종목명</th>
                <th>수량</th>
                <th>매수가</th>
                <th>목표가</th>
                <th>손절가</th>
            </tr>
            {position_rows}
        </table>
    </div>

    <div class="card">
        <h2>주문 상태 요약</h2>
        <table>
            <tr>
                <th>상태</th>
                <th>건수</th>
            </tr>
            {order_status_rows}
        </table>
    </div>

    <div class="card">
        <h2>최근 주문</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>종목명</th>
                <th>액션</th>
                <th>수량</th>
                <th>가격</th>
                <th>상태</th>
            </tr>
            {recent_order_rows}
        </table>
    </div>

    <div class="card">
        <h2>최근 자동매매 로그</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>이벤트</th>
                <th>메시지</th>
                <th>시각</th>
            </tr>
            {log_rows}
        </table>
    </div>

</div>
</body>
</html>
"""

    return HTMLResponse(content=html)
