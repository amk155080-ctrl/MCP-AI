from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.asset_service import AssetService
from app.services.allocation_service import AllocationService
from app.services.asset_health_service import AssetHealthService
from app.services.rebalance_service import RebalanceService
from app.services.retirement_service import RetirementService
from app.services.asset_report_service import AssetReportService
from app.services.kis_asset_sync_service import KisAssetSyncService
from app.scheduler.asset_scheduler import run_asset_daily_all


router = APIRouter(
    prefix="/api/v14",
    tags=["MCP 14 Asset Management"]
)


@router.get("/assets")
def get_assets(db: Session = Depends(get_db)):
    return {
        "found": True,
        "version": "MCP 14.0",
        "items": AssetService.get_all_assets(db)
    }


@router.get("/summary")
def get_asset_summary(db: Session = Depends(get_db)):
    summary = AssetService.get_summary(db)

    return {
        "found": True,
        "version": "MCP 14.1",
        "summary": summary,
        "message": "총자산 요약 조회 완료"
    }


@router.get("/allocation")
def get_asset_allocation(db: Session = Depends(get_db)):
    summary = AssetService.get_summary(db)
    allocation = AllocationService.analyze(summary)

    return {
        "found": True,
        "version": "MCP 14.2",
        "allocation": allocation,
        "message": "자산배분 분석 완료"
    }


@router.get("/health")
def get_asset_health(db: Session = Depends(get_db)):
    summary = AssetService.get_summary(db)
    allocation = AllocationService.analyze(summary)
    health = AssetHealthService.evaluate(allocation)

    return {
        "found": True,
        "version": "MCP 14.3",
        "health": health,
        "message": "자산건전성 평가 완료"
    }


@router.get("/rebalance")
def get_asset_rebalance(db: Session = Depends(get_db)):
    summary = AssetService.get_summary(db)
    rebalance = RebalanceService.recommend(summary)

    return {
        "found": True,
        "version": "MCP 14.4",
        "rebalance": rebalance,
        "message": "리밸런싱 추천 완료"
    }


@router.get("/retirement")
def get_retirement_simulation(
    current_asset: float = Query(100000000),
    annual_return: float = Query(0.07),
    years: int = Query(20)
):
    result = RetirementService.simulate(
        current_asset=current_asset,
        annual_return=annual_return,
        years=years
    )

    return {
        "found": True,
        "version": "MCP 14.5",
        "retirement": result,
        "message": "은퇴 시뮬레이션 완료"
    }

@router.get("/dashboard")
def get_asset_dashboard(db: Session = Depends(get_db)):
    summary = AssetService.get_summary(db)
    allocation = AllocationService.analyze(summary)
    health = AssetHealthService.evaluate(allocation)
    rebalance = RebalanceService.recommend(summary)

    dashboard = AssetReportService.make_dashboard(
        summary=summary,
        allocation=allocation,
        health=health,
        rebalance=rebalance,
    )

    return {
        "found": True,
        "version": "MCP 14.6",
        "dashboard": dashboard,
        "message": "자산관리 대시보드 생성 완료",
    }


@router.get("/kakao")
def get_asset_kakao_report(db: Session = Depends(get_db)):
    summary = AssetService.get_summary(db)
    allocation = AllocationService.analyze(summary)
    health = AssetHealthService.evaluate(allocation)
    rebalance = RebalanceService.recommend(summary)

    kakao = AssetReportService.make_kakao_report(
        summary=summary,
        allocation=allocation,
        health=health,
        rebalance=rebalance,
    )

    return {
        "found": True,
        "version": "MCP 14.7",
        "kakao": kakao,
        "message": "자산관리 카카오 리포트 생성 완료",
    }

@router.get("/sync")
def sync_kis_assets(db: Session = Depends(get_db)):
    result = KisAssetSyncService.sync(db)

    return {
        "found": True,
        "version": "MCP 14.8",
        "sync": result,
        "message": "KIS 계좌 자산을 MCP14 자산 테이블에 동기화 완료",
    }

@router.get("/schedule/run")
def run_asset_schedule_now():
    result = run_asset_daily_all()

    return {
        "found": True,
        "version": "MCP 14.9",
        "schedule": result,
        "message": "자산관리 스케줄 수동 실행 완료",
    }
