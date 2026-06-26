from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import requests

load_dotenv()

KIS_APP_KEY = os.getenv("KIS_APP_KEY")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET")
KIS_BASE_URL = os.getenv("KIS_BASE_URL", "https://openapi.koreainvestment.com:9443")

_cached_token = None
_cached_expired_at = None


def get_kis_access_token():
    global _cached_token, _cached_expired_at

    now = datetime.now()

    if _cached_token and _cached_expired_at and now < _cached_expired_at:
        return {
            "found": True,
            "access_token": _cached_token,
            "cached": True,
            "expired_at": _cached_expired_at.isoformat()
        }

    url = f"{KIS_BASE_URL}/oauth2/tokenP"

    payload = {
        "grant_type": "client_credentials",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET
    }

    response = requests.post(url, json=payload, timeout=10)

    try:
        data = response.json()
    except Exception:
        data = {"raw": response.text}

    if response.status_code != 200 or not data.get("access_token"):
        return {
            "found": False,
            "status_code": response.status_code,
            "response": data
        }

    _cached_token = data["access_token"]
    _cached_expired_at = now + timedelta(seconds=int(data.get("expires_in", 86400)) - 300)

    return {
        "found": True,
        "access_token": _cached_token,
        "cached": False,
        "expired_at": _cached_expired_at.isoformat()
    }
