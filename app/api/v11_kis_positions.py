from fastapi import APIRouter

from app.api.v11_kis_balance import get_kis_balance

router = APIRouter(
    prefix="/api/v11/kis",
    tags=["MCP 11.2 KIS Positions"]
)


def to_int(value):
    try:
        return int(str(value).replace(",", "").strip())
    except:
        return 0


def to_float(value):
    try:
        return float(str(value).replace(",", "").strip())
    except:
        return 0.0


@router.get("/positions")
def get_kis_positions():
    balance = get_kis_balance()

    if not balance.get("found"):
        return {
            "found": False,
            "version": "MCP 11.2",
            "message": "KIS 잔고 조회 실패",
            "balance": balance
        }

    output1 = balance.get("output1") or []
    output2 = balance.get("output2") or []

    positions = []

    for item in output1:
        quantity = to_int(item.get("hldg_qty"))
        current_price = to_int(item.get("prpr"))
        eval_amount = to_int(item.get("evlu_amt"))
        buy_amount = to_int(item.get("pchs_amt"))
        profit_loss = to_int(item.get("evlu_pfls_amt"))
        profit_rate = to_float(item.get("evlu_pfls_rt"))

        positions.append({
            "stock_code": item.get("pdno"),
            "stock_name": item.get("prdt_name"),
            "quantity": quantity,
            "buy_average_price": to_float(item.get("pchs_avg_pric")),
            "current_price": current_price,
            "buy_amount": buy_amount,
            "eval_amount": eval_amount,
            "profit_loss": profit_loss,
            "profit_rate": profit_rate
        })

    summary = output2[0] if output2 else {}

    return {
        "found": True,
        "version": "MCP 11.2",
        "position_count": len(positions),
        "positions": positions,
        "summary": {
            "cash": to_int(summary.get("dnca_tot_amt")),
            "stock_eval_amount": to_int(summary.get("scts_evlu_amt")),
            "total_eval_amount": to_int(summary.get("tot_evlu_amt")),
            "net_asset": to_int(summary.get("nass_amt")),
            "total_profit_loss": to_int(summary.get("evlu_pfls_smtl_amt")),
            "asset_change_rate": to_float(summary.get("asst_icdc_erng_rt"))
        },
        "message": "KIS 보유종목 정리 완료"
    }
