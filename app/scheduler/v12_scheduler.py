from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from app.api.v12_auto_trading import (
    run_auto_buy,
    run_monitor,
    run_market_close,
    get_auto_trading_report,
)


scheduler = BackgroundScheduler(timezone="Asia/Seoul")


def safe_run(job_name, func):
    try:
        print(f"[MCP 12.11] {job_name} 시작: {datetime.now()}")
        result = func()
        print(f"[MCP 12.11] {job_name} 완료: {result}")
    except Exception as e:
        print(f"[MCP 12.11] {job_name} 오류: {e}")


def start_v12_scheduler():
    if scheduler.running:
        print("[MCP 12.11] 스케줄러 이미 실행 중")
        return

    scheduler.add_job(
        lambda: safe_run("08:50 자동매수 준비", run_auto_buy),
        CronTrigger(day_of_week="mon-fri", hour=8, minute=50),
        id="v12_auto_buy",
        replace_existing=True,
    )

    for hour, minute in [(10, 0), (11, 0), (13, 0), (14, 0), (15, 0)]:
        scheduler.add_job(
            lambda h=hour, m=minute: safe_run(f"{h:02d}:{m:02d} 장중 모니터링", run_monitor),
            CronTrigger(day_of_week="mon-fri", hour=hour, minute=minute),
            id=f"v12_monitor_{hour}_{minute}",
            replace_existing=True,
        )

    scheduler.add_job(
        lambda: safe_run("15:20 장마감 정리", run_market_close),
        CronTrigger(day_of_week="mon-fri", hour=15, minute=20),
        id="v12_market_close",
        replace_existing=True,
    )

    scheduler.add_job(
        lambda: safe_run("15:30 자동 리포트", get_auto_trading_report),
        CronTrigger(day_of_week="mon-fri", hour=15, minute=30),
        id="v12_daily_report",
        replace_existing=True,
    )

    scheduler.start()
    print("[MCP 12.11] 스케줄러 시작 완료")


def get_v12_scheduler_status():
    jobs = []

    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "next_run_time": str(job.next_run_time),
        })

    return {
        "running": scheduler.running,
        "job_count": len(jobs),
        "jobs": jobs,
    }


def stop_v12_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        return True
    return False
