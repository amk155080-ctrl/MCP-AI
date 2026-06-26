from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.auction_asset import AuctionAsset

from app.services.auction_ai_engine.rights_analyzer import RightsAnalyzer
from app.services.auction_ai_engine.eviction_analyzer import EvictionAnalyzer
from app.services.auction_ai_engine.bid_predictor import BidPredictor
from app.services.auction_ai_engine.risk_engine import AuctionRiskEngine
from app.services.auction_ai_engine.committee import AuctionCommittee
from app.services.auction_ai_engine.report_builder import AuctionEngineReportBuilder


router = APIRouter(
    prefix="/api/v15/auction/engine",
    tags=["MCP 15 Auction AI Engine"]
)


def _get_auction(db: Session, auction_id: int):
    return (
        db.query(AuctionAsset)
        .filter(AuctionAsset.id == auction_id)
        .first()
    )


def _run_engine(db: Session, auction_id: int):
    auction = _get_auction(db, auction_id)

    if not auction:
        return None

    rights = RightsAnalyzer.analyze(auction, db)
    eviction = EvictionAnalyzer.analyze(auction, db)
    bid = BidPredictor.predict(auction)
    risk = AuctionRiskEngine.evaluate(
        auction=auction,
        rights_result=rights,
        eviction_result=eviction,
        bid_result=bid,
    )
    committee = AuctionCommittee.decide(
        auction=auction,
        rights_result=rights,
        eviction_result=eviction,
        bid_result=bid,
        risk_result=risk,
    )

    report = AuctionEngineReportBuilder.build(
        auction=auction,
        rights=rights,
        eviction=eviction,
        bid=bid,
        risk=risk,
        committee=committee,
    )

    return report


@router.get("/analyze/{auction_id}")
def analyze_auction(
    auction_id: int,
    db: Session = Depends(get_db)
):
    result = _run_engine(db, auction_id)

    if result is None:
        return {
            "found": False,
            "version": "MCP 15.7~15.12",
            "message": "경매 물건을 찾을 수 없습니다.",
        }

    return {
        "found": True,
        "version": "MCP 15.7~15.12",
        "analysis": result,
        "message": "Auction AI Engine 분석 완료",
    }


@router.get("/final-opinion/{auction_id}")
def final_opinion(
    auction_id: int,
    db: Session = Depends(get_db)
):
    result = _run_engine(db, auction_id)

    if result is None:
        return {
            "found": False,
            "version": "MCP 15.7~15.12",
            "message": "경매 물건을 찾을 수 없습니다.",
        }

    return {
        "found": True,
        "version": "MCP 15.9",
        "final": result.get("summary"),
        "committee": result.get("committee"),
        "message": "Auction AI Engine 최종 의견 생성 완료",
    }


@router.get("/report/{auction_id}")
def auction_engine_report(
    auction_id: int,
    db: Session = Depends(get_db)
):
    result = _run_engine(db, auction_id)

    if result is None:
        return {
            "found": False,
            "version": "MCP 15.10",
            "message": "경매 물건을 찾을 수 없습니다.",
        }

    kakao = AuctionEngineReportBuilder.kakao(result)

    return {
        "found": True,
        "version": "MCP 15.10",
        "report": result,
        "kakao": kakao,
        "message": "Auction AI Engine 리포트 생성 완료",
    }


@router.get("/all")
def analyze_all_auctions(
    db: Session = Depends(get_db)
):
    rows = (
        db.query(AuctionAsset)
        .order_by(AuctionAsset.id.asc())
        .all()
    )

    results = []

    for row in rows:
        result = _run_engine(db, row.id)
        if result:
            results.append(result)

    return {
        "found": True,
        "version": "MCP 15.7~15.12",
        "count": len(results),
        "items": results,
        "message": "전체 경매 물건 Auction AI Engine 분석 완료",
    }
