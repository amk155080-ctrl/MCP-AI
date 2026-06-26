from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, datetime
from decimal import Decimal

from app.core.database import get_db

router = APIRouter(
    prefix="/api/v8/report/daily/html",
    tags=["MCP 8.11 Daily Report HTML"],
)


def fmt(value):
    if value is None:
        return "-"
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return f"{float(value):,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        return f"{value:,.2f}"
    return str(value)


def make_html(item):
    return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>MCP 일일 투자 리포트</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #f4f6f8;
            margin: 0;
            padding: 30px;
            color: #222;
        }}
        .container {{
            max-width: 980px;
            margin: auto;
            background: white;
            border-radius: 18px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        }}
        .badge {{
            display: inline-block;
            padding: 8px 14px;
            border-radius: 999px;
            background: #eef3ff;
            font-weight: 700;
            margin-bottom: 12px;
        }}
        h1 {{
            margin: 8px 0 10px;
            font-size: 30px;
        }}
        .headline {{
            font-size: 20px;
            font-weight: 700;
            margin: 18px 0;
            color: #0f3d91;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 14px;
            margin: 24px 0;
        }}
        .card {{
            background: #f8fafc;
            border-radius: 14px;
            padding: 18px;
            border: 1px solid #e6eaf0;
        }}
        .label {{
            font-size: 13px;
            color: #667085;
            margin-bottom: 6px;
        }}
        .value {{
            font-size: 22px;
            font-weight: 800;
        }}
        .section {{
            margin-top: 26px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
        }}
        pre {{
            white-space: pre-wrap;
            background: #111827;
            color: #f9fafb;
            padding: 18px;
            border-radius: 12px;
            line-height: 1.6;
        }}
        .footer {{
            margin-top: 24px;
            color: #667085;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="badge">{fmt(item.get("version"))}</div>
        <h1>{fmt(item.get("title"))}</h1>
        <div class="headline">{fmt(item.get("headline"))}</div>

        <div class="grid">
            <div class="card">
                <div class="label">거래일</div>
                <div class="value">{fmt(item.get("trade_date"))}</div>
            </div>
            <div class="card">
                <div class="label">전략 등급</div>
                <div class="value">{fmt(item.get("strategy_grade"))}</div>
            </div>
            <div class="card">
                <div class="label">최종 실행 판단</div>
                <div class="value">{fmt(item.get("final_execution"))}</div>
            </div>
            <div class="card">
                <div class="label">TOP PICK</div>
                <div class="value">{fmt(item.get("top_stock_name"))}</div>
            </div>
            <div class="card">
                <div class="label">안전 주문금액</div>
                <div class="value">{fmt(item.get("safe_total_order_amount"))}원</div>
            </div>
            <div class="card">
                <div class="label">현금</div>
                <div class="value">{fmt(item.get("cash"))}원</div>
            </div>
            <div class="card">
                <div class="label">원래 예상 손실률</div>
                <div class="value">{fmt(item.get("raw_portfolio_loss_percent"))}%</div>
            </div>
            <div class="card">
                <div class="label">안전 예상 손실률</div>
                <div class="value">{fmt(item.get("safe_portfolio_loss_percent"))}%</div>
            </div>
        </div>

        <div class="section">
            <h2>요약</h2>
            <p>{fmt(item.get("summary"))}</p>
        </div>

        <div class="section">
            <h2>리스크 요약</h2>
            <p>{fmt(item.get("risk_summary"))}</p>
        </div>

        <div class="section">
            <h2>알림 요약</h2>
            <p>{fmt(item.get("alert_summary"))}</p>
        </div>

        <div class="section">
            <h2>카카오톡 공유 메시지</h2>
            <pre>{fmt(item.get("kakao_message"))}</pre>
        </div>

        <div class="footer">
            생성 시각: {fmt(item.get("created_at"))}
        </div>
    </div>
</body>
</html>
"""


def fetch_latest(db: Session):
    return db.execute(
        text("""
            SELECT *
            FROM mcp4.daily_report_log
            ORDER BY id DESC
            LIMIT 1
        """)
    ).mappings().first()


def fetch_by_id(db: Session, log_id: int):
    return db.execute(
        text("""
            SELECT *
            FROM mcp4.daily_report_log
            WHERE id = :log_id
        """),
        {"log_id": log_id},
    ).mappings().first()


@router.get("/latest", response_class=HTMLResponse)
def daily_report_html_latest(db: Session = Depends(get_db)):
    row = fetch_latest(db)

    if not row:
        return HTMLResponse(
            content="<h1>저장된 일일 투자 리포트가 없습니다.</h1>",
            status_code=404,
        )

    return HTMLResponse(content=make_html(dict(row)))


@router.get("/{log_id}", response_class=HTMLResponse)
def daily_report_html_by_id(log_id: int, db: Session = Depends(get_db)):
    row = fetch_by_id(db, log_id)

    if not row:
        raise HTTPException(status_code=404, detail="해당 리포트를 찾을 수 없습니다.")

    return HTMLResponse(content=make_html(dict(row)))
