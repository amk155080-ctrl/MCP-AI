def calculate_rights_score(
    base_right: str,
    tenant_priority: str,
    occupancy: str,
    takeover_amount: int,
    legal_risk_count: int,
) -> dict:
    score = 100

    if base_right == "말소기준권리 없음":
        score -= 35

    if "대항력 있음" in tenant_priority:
        score -= 30

    if "배당요구 없음" in tenant_priority:
        score -= 20

    if occupancy not in ["소유자 점유", "임차인 없음"]:
        score -= 10

    if takeover_amount > 0:
        score -= min(30, takeover_amount // 10_000_000)

    score -= legal_risk_count * 10
    score = max(0, min(100, score))

    if score >= 80:
        risk_level = "LOW"
        recommendation = "입찰 가능"
    elif score >= 60:
        risk_level = "MEDIUM"
        recommendation = "주의 후 입찰"
    else:
        risk_level = "HIGH"
        recommendation = "입찰 보류"

    return {
        "rights_score": score,
        "risk_level": risk_level,
        "recommendation": recommendation,
    }
