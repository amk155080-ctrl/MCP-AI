from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.api.v9_position_monitor import position_monitor

router = APIRouter(
    prefix="/api/v9",
    tags=["MCP 9.5 Position Monitor HTML"]
)


@router.get("/position-monitor/html", response_class=HTMLResponse)
def position_monitor_html():

    data = position_monitor()

    if not data.get("found"):
        return HTMLResponse("<h1>데이터 없음</h1>")

    rows = ""

    for p in data["positions"]:

        if p["action"] == "SELL":
            color = "#ffdddd"

        elif p["action"] == "TAKE_PROFIT":
            color = "#fff3cd"

        else:
            color = "#ddffdd"

        rows += f"""
        <tr style="background:{color}">
            <td>{p['stock_code']}</td>
            <td>{p['stock_name']}</td>
            <td>{p['current_price']:,}</td>
            <td>{p['profit_rate']}%</td>
            <td>{p['target_reached']}</td>
            <td>{p['stop_broken']}</td>
            <td>{p['action']}</td>
        </tr>
        """

    html = f"""
    <html>
    <head>
        <title>MCP 9.5 Position Dashboard</title>

        <style>

        body {{
            font-family: Arial;
            background:#f4f6f9;
            margin:40px;
        }}

        .card {{
            background:white;
            padding:25px;
            border-radius:15px;
            box-shadow:0 0 10px rgba(0,0,0,0.1);
        }}

        table {{
            width:100%;
            border-collapse:collapse;
        }}

        th,td {{
            padding:12px;
            border-bottom:1px solid #ddd;
        }}

        h1 {{
            color:#1f4e79;
        }}

        </style>

    </head>

    <body>

    <div class="card">

    <h1>📊 MCP 9.5 실시간 포지션 대시보드</h1>

    <h3>총 투자금 : {data['total_buy_amount']:,.0f} 원</h3>

    <h3>평가금액 : {data['total_current_value']:,.0f} 원</h3>

    <h3>평가손익 : {data['total_profit_loss']:,.0f} 원</h3>

    <h3>수익률 : {data['total_profit_rate']}%</h3>

    <br>

    <table>

    <tr>
        <th>종목코드</th>
        <th>종목명</th>
        <th>현재가</th>
        <th>수익률</th>
        <th>목표가도달</th>
        <th>손절이탈</th>
        <th>액션</th>
    </tr>

    {rows}

    </table>

    </div>

    </body>
    </html>
    """

    return HTMLResponse(html)
