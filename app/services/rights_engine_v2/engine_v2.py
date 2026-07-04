from app.services.rights_engine_v2.score_v2 import calculate_rights_score
from app.services.rights_engine_v2.summary_v2 import build_rights_summary


def _detect_base_right(text: str) -> str:
    base_keywords = ["근저당", "저당권", "압류", "가압류", "담보가등기", "경매개시결정"]

    for keyword in base_keywords:
        if keyword in text:
            return keyword

    return "말소기준권리 없음"


def _detect_tenant_priority(text: str) -> str:
    if "임차인 없음" in text or "임차인 없는" in text:
        return "임차인 없음"

    has_opposing_power = any(
        keyword in text
        for keyword in ["대항력 있음", "전입신고", "주민등록"]
    )

    has_fixed_date = any(
        keyword in text
        for keyword in ["확정일자", "우선변제권"]
    )

    has_distribution_request = any(
        keyword in text
        for keyword in ["배당요구", "배당신청"]
    )

    if has_opposing_power and not has_distribution_request:
        return "대항력 있음 / 배당요구 없음"

    if has_opposing_power and has_distribution_request:
        return "대항력 있음 / 배당요구 있음"

    if has_fixed_date:
        return "우선변제 가능성 있음"

    return "임차인 권리 불명"


def _detect_occupancy(text: str) -> str:
    if "소유자 점유" in text:
        return "소유자 점유"

    if "임차인 없음" in text:
        return "임차인 없음"

    if "임차인 점유" in text or "점유자" in text:
        return "임차인 또는 점유자 점유"

    return "점유상태 불명"


def _estimate_takeover_amount(text: str, tenant_priority: str) -> int:
    if "임차인 없음" in tenant_priority:
        return 0

    if "대항력 있음" in tenant_priority and "배당요구 없음" in tenant_priority:
        return 30_000_000

    if "대항력 있음" in tenant_priority:
        return 10_000_000

    return 0


def _detect_legal_risks(text: str) -> list:
    risk_keywords = [
        "유치권",
        "법정지상권",
        "분묘기지권",
        "예고등기",
        "가처분",
        "가등기",
        "임금채권",
        "체납",
    ]

    return [keyword for keyword in risk_keywords if keyword in text]


def analyze(text: str) -> dict:
    if not text or not text.strip():
        return {
            "version": "MCP16-RIGHTS-ENGINE-2.0",
            "error": "분석할 텍스트가 없습니다.",
        }

    base_right = _detect_base_right(text)
    tenant_priority = _detect_tenant_priority(text)
    occupancy = _detect_occupancy(text)
    takeover_amount = _estimate_takeover_amount(text, tenant_priority)
    legal_risks = _detect_legal_risks(text)

    score_result = calculate_rights_score(
        base_right=base_right,
        tenant_priority=tenant_priority,
        occupancy=occupancy,
        takeover_amount=takeover_amount,
        legal_risk_count=len(legal_risks),
    )

    result = {
        "version": "MCP16-RIGHTS-ENGINE-2.0",
        "base_right": base_right,
        "tenant_priority": tenant_priority,
        "occupancy": occupancy,
        "lease_deposit": 0,
        "takeover_amount": takeover_amount,
        "takeover_required": takeover_amount > 0,
        "legal_risks": legal_risks,
        "legal_risk_count": len(legal_risks),
        **score_result,
    }

    result["summary"] = build_rights_summary(result)

    return result
