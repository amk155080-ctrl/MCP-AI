from fastapi import APIRouter

from app.scheduler.v12_scheduler import (
    start_v12_scheduler,
    get_v12_scheduler_status,
    stop_v12_scheduler,
)

router = APIRouter(
    prefix="/api/v12/scheduler",
    tags=["MCP 12.11 Scheduler"]
)


@router.post("/start")
def start_scheduler():
    start_v12_scheduler()

    return {
        "started": True,
        "version": "MCP 12.11",
        "status": get_v12_scheduler_status(),
        "message": "MCP 12 자동 실행 스케줄러 시작 완료"
    }


@router.get("/status")
def scheduler_status():
    return {
        "found": True,
        "version": "MCP 12.11",
        "status": get_v12_scheduler_status(),
        "message": "스케줄러 상태 조회 완료"
    }


@router.post("/stop")
def stop_scheduler():
    stopped = stop_v12_scheduler()

    return {
        "stopped": stopped,
        "version": "MCP 12.11",
        "message": "스케줄러 중지 완료" if stopped else "실행 중인 스케줄러가 없습니다."
    }

