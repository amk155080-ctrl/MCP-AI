from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v8/report/html",
    tags=["MCP 8.11 Report HTML"]
)


@router.get("/latest", response_class=HTMLResponse)
def report_html_latest():

    db = SessionLocal()

    try:

        row = db.execute(
            text("""
                SELECT *
                FROM mcp4.daily_report_log
                ORDER BY id DESC
                LIMIT 1
            """)
        ).mappings().first()

        if not row:
            return HTMLResponse("<h1>저장된 리포트가 없습니다.</h1>")

        html = f"""
        <html>
        <head>
            <title>MCP 투자 리포트</title>
            <style>
                body {{
                    font-family: Arial;
                    margin:40px;
                    background:#f4f6f9;
                }}

                .box {{
                    background:white;
                    padding:30px;
                    border-radius:15px;
                    box-shadow:0 0 10px rgba(0,0,0,0.1);
                }}

                h1 {{
                    color:#1f4e79;
                }}

                table {{
                    width:100%;
                    border-collapse:collapse;
                }}

                td {{
                    padding:10px;
                    border-bottom:1px solid #ddd;
                }}
            </style>
        </head>

        <body>

        <div class="box">

        <h1>📊 MCP 일일 투자 리포트</h1>

        <table>

        <tr><td>전략등급</td><td>{row["strategy_grade"]}</td></tr>
        <tr><td>실행판단</td><td>{row["final_execution"]}</td></tr>
        <tr><td>TOP PICK</td><td>{row["top_stock_name"]}</td></tr>
        <tr><td>안전 주문금액</td><td>{row["safe_total_order_amount"]:,}원</td></tr>
        <tr><td>현금</td><td>{row["cash"]:,}원</td></tr>
        <tr><td>원래 손실률</td><td>{row["raw_portfolio_loss_percent"]}%</td></tr>
        <tr><td>안전 손실률</td><td>{row["safe_portfolio_loss_percent"]}%</td></tr>
        <tr><td>알림상태</td><td>{row["alert_level"]}</td></tr>

        </table>

        <h2>요약</h2>
        <p>{row["summary"]}</p>

        <h2>리스크 요약</h2>
        <p>{row["risk_summary"]}</p>

        <h2>알림 요약</h2>
        <p>{row["alert_summary"]}</p>

        </div>

        </body>
        </html>
        """

        return HTMLResponse(html)

    finally:
        db.close()
