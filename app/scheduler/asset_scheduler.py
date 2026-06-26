import requests
from datetime import datetime


BASE_URL = "http://127.0.0.1:8000"


def run_asset_sync():
    try:
        url = f"{BASE_URL}/api/v14/sync"
        response = requests.get(url, timeout=15)

        return {
            "job": "asset_sync",
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "time": str(datetime.now()),
            "result": response.json()
        }

    except Exception as e:
        return {
            "job": "asset_sync",
            "success": False,
            "time": str(datetime.now()),
            "error": str(e)
        }


def run_asset_dashboard():
    try:
        url = f"{BASE_URL}/api/v14/dashboard"
        response = requests.get(url, timeout=15)

        return {
            "job": "asset_dashboard",
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "time": str(datetime.now()),
            "result": response.json()
        }

    except Exception as e:
        return {
            "job": "asset_dashboard",
            "success": False,
            "time": str(datetime.now()),
            "error": str(e)
        }


def run_asset_kakao():
    try:
        url = f"{BASE_URL}/api/v14/kakao"
        response = requests.get(url, timeout=15)

        return {
            "job": "asset_kakao",
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "time": str(datetime.now()),
            "result": response.json()
        }

    except Exception as e:
        return {
            "job": "asset_kakao",
            "success": False,
            "time": str(datetime.now()),
            "error": str(e)
        }


def run_asset_daily_all():
    sync_result = run_asset_sync()
    dashboard_result = run_asset_dashboard()
    kakao_result = run_asset_kakao()

    return {
        "version": "MCP 14.9",
        "title": "MCP 자산관리 일일 자동 실행",
        "time": str(datetime.now()),
        "sync": sync_result,
        "dashboard": dashboard_result,
        "kakao": kakao_result,
        "message": "MCP 14.9 자산관리 자동 실행 완료"
    }
