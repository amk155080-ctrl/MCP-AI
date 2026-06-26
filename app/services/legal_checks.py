import re


LEGAL_CHECK_VERSION = "MCP16.4-LEGAL-CHECKS-1.1"


def _contains_any(text: str, keywords):
    lower = (text or "").lower()

    for keyword in keywords:
        if keyword.lower() in lower:
            return keyword

    return None


def _result(exists: bool, reason: str = "", risk: int = 0):
    return {
        "exists": exists,
        "reason": reason,
        "risk": risk,
    }


def detect_statutory_surface_right(text: str):
    """
    법정지상권 감지
    """

    keywords = [
        "법정지상권",
        "statutory surface right",
        "지상권",
    ]

    found = _contains_any(text, keywords)

    if found:
        return _result(True, found, 60)

    return _result(False)


def detect_lien(text: str):
    """
    유치권 감지
    """

    keywords = [
        "유치권",
        "lien",
        "유치권신고",
        "유치권 신고",
        "유치권 행사",
        "공사대금",
        "점유 유치",
    ]

    found = _contains_any(text, keywords)

    if found:
        return _result(True, found, 70)

    return _result(False)


def detect_preliminary_registration(text: str):
    """
    예고등기 감지
    """

    keywords = [
        "예고등기",
        "preliminary registration",
    ]

    found = _contains_any(text, keywords)

    if found:
        return _result(True, found, 90)

    return _result(False)


def detect_provisional_disposition(text: str):
    """
    가처분 감지
    """

    keywords = [
        "가처분",
        "처분금지가처분",
        "provisional disposition",
    ]

    found = _contains_any(text, keywords)

    if found:
        return _result(True, found, 60)

    return _result(False)


def detect_provisional_registration(text: str):
    """
    가등기 감지
    """

    keywords = [
        "가등기",
        "소유권이전청구권가등기",
        "담보가등기",
        "provisional registration",
    ]

    found = _contains_any(text, keywords)

    if found:
        return _result(True, found, 50)

    return _result(False)


def detect_co_ownership(text: str):
    """
    공유지분 감지
    """

    keywords = [
        "공유지분",
        "지분매각",
        "공유자",
        "지분",
        "co-ownership",
        "co ownership",
        "shared ownership",
    ]

    found = _contains_any(text, keywords)

    if found:
        return _result(True, found, 40)

    return _result(False)


def detect_senior_leasehold(text: str):
    """
    선순위 전세권 감지
    """

    keywords = [
        "선순위 전세권",
        "전세권",
        "전세권설정",
        "senior leasehold",
        "leasehold",
    ]

    found = _contains_any(text, keywords)

    if found:
        return _result(True, found, 50)

    return _result(False)


def detect_dividend_deadline(text: str):
    """
    배당요구 종기 감지
    """

    lower = (text or "").lower()

    patterns = [
        r"배당요구\s*종기",
        r"배당요구종기",
        r"dividend\s*deadline",
        r"distribution\s*deadline",
    ]

    for pattern in patterns:
        if re.search(pattern, lower):
            return _result(True, pattern, 20)

    return _result(False)


def detect_occupant_type(text: str):
    """
    점유자 유형 감지
    """

    lower = (text or "").lower()

    if "occupancy: owner" in lower or "소유자 점유" in text or "소유자" in text:
        return {
            "type": "OWNER",
            "label": "소유자 점유",
            "risk": 5,
        }

    if "occupancy: tenant" in lower or "임차인 점유" in text or "임차인" in text:
        return {
            "type": "TENANT",
            "label": "임차인 점유",
            "risk": 20,
        }

    if "occupancy: vacant" in lower or "공실" in text:
        return {
            "type": "VACANT",
            "label": "공실",
            "risk": 0,
        }

    if "무단점유" in text or "무단 점유" in text:
        return {
            "type": "UNAUTHORIZED",
            "label": "무단 점유",
            "risk": 50,
        }

    if "법인" in text or "회사" in text:
        return {
            "type": "CORPORATE",
            "label": "법인 점유 가능성",
            "risk": 45,
        }

    return {
        "type": "UNKNOWN",
        "label": "점유자 미확인",
        "risk": 20,
    }


def detect_eviction_difficulty(text: str):
    """
    명도 난이도 감지
    """

    occupant = detect_occupant_type(text)

    occupant_type = occupant.get("type")

    if occupant_type == "VACANT":
        return {
            "level": "EASY",
            "label": "공실로 명도 부담 낮음",
            "risk": 0,
        }

    if occupant_type == "OWNER":
        return {
            "level": "NORMAL",
            "label": "소유자 점유로 일반 명도 수준",
            "risk": 10,
        }

    if occupant_type == "TENANT":
        return {
            "level": "HARD",
            "label": "임차인 점유로 명도 확인 필요",
            "risk": 30,
        }

    if occupant_type == "UNAUTHORIZED":
        return {
            "level": "VERY_HARD",
            "label": "무단 점유로 명도 난이도 높음",
            "risk": 60,
        }

    if occupant_type == "CORPORATE":
        return {
            "level": "VERY_HARD",
            "label": "법인 점유 가능성으로 명도 난이도 높음",
            "risk": 50,
        }

    return {
        "level": "UNKNOWN",
        "label": "명도 난이도 미확인",
        "risk": 25,
    }


def run_all_legal_checks(text: str):
    """
    모든 법률 위험 요소 통합 실행
    """

    return {
        "version": LEGAL_CHECK_VERSION,
        "statutory_surface_right": detect_statutory_surface_right(text),
        "lien": detect_lien(text),
        "preliminary_registration": detect_preliminary_registration(text),
        "provisional_disposition": detect_provisional_disposition(text),
        "provisional_registration": detect_provisional_registration(text),
        "co_ownership": detect_co_ownership(text),
        "senior_leasehold": detect_senior_leasehold(text),
        "dividend_deadline": detect_dividend_deadline(text),
        "occupant_type": detect_occupant_type(text),
        "eviction_difficulty": detect_eviction_difficulty(text),
    }
