import requests
from app.core.config import settings


def get_access_token():
    url = f"{settings.KIS_BASE_URL}/oauth2/tokenP"

    payload = {
        "grant_type": "client_credentials",
        "appkey": settings.KIS_APP_KEY,
        "appsecret": settings.KIS_APP_SECRET,
    }

    r = requests.post(url, json=payload, timeout=30)

    if r.status_code != 200:
        raise RuntimeError(f"KIS token failed {r.status_code}: {r.text}")

    data = r.json()
    return data["access_token"]


def kis_get(path, tr_id, params):
    token = get_access_token()

    url = f"{settings.KIS_BASE_URL}{path}"

    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": settings.KIS_APP_KEY,
        "appsecret": settings.KIS_APP_SECRET,
        "tr_id": tr_id,
        "custtype": "P",
    }

    r = requests.get(url, headers=headers, params=params, timeout=30)

    if r.status_code != 200:
        raise RuntimeError(f"KIS GET failed {r.status_code}: {r.text}")

    return r.json()
