from fastapi import APIRouter
from datetime import datetime


router = APIRouter(
    prefix="/api/v15",
    tags=["MCP15 Morning Brief"],
)


def build_market_summary() -> dict:
    return {
        "market_status": "중립",
        "kospi_signal": "확인 필요",
        "sox_signal": "확인 필요",
        "exchange_rate_signal": "확인 필요",
        "comment": "시장 데이터 연동 전 기본 브리핑입니다.",
    }


def build_top_candidates() -> list:
    return [
        {
            "rank": 1,
            "stock_code": "052690",
            "stock_name": "한전기술",
            "score": 70,
            "signal": "HOLD",
            "comment": "기존 MCP 추천 결과 기반 샘플 후보입니다.",
        }
    ]


def build_risk_summary() -> dict:
    return {
        "risk_level": "LOW",
        "max_loss_limit": "5%",
        "comment": "리스크 한도 내에서만 분할 매수 검토가 필요합니다.",
    }


def build_final_opinion() -> dict:
    return {
        "final_opinion": "보유",
        "action": "무리한 신규 매수보다 시장 확인 후 분할 접근",
        "comment": "현재는 시장 방향성과 종목별 신호를 함께 확인하는 단계입니다.",
    }


@router.get("/morning-brief")
def morning_brief():
    market = build_market_summary()
    candidates = build_top_candidates()
    risk = build_risk_summary()
    final_opinion = build_final_opinion()

    return {
        "found": True,
        "version": "MCP 15.1",
        "title": "MCP15 아침 AI 투자 브리핑",
        "created_at": datetime.now().isoformat(),
        "market": market,
        "top_candidates": candidates,
        "risk": risk,
        "final_opinion": final_opinion,
        "summary": (
            f"오늘 시장상황은 {market['market_status']}입니다. "
            f"추천 후보는 {len(candidates)}개이며, "
            f"최종 의견은 {final_opinion['final_opinion']}입니다."
        ),
        "message": "아침 투자 브리핑 생성 완료",
    }
