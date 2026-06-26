from typing import Dict


class RightsRiskEngine:

    VERSION = "MCP16.4-RISK-1.1"

    def calculate(self, rights: Dict) -> Dict:

        score = 0
        reasons = []

        base_right = rights.get("base_right", "")

        if base_right == "근저당":
            score += 5
        elif base_right == "압류":
            score += 15
        elif base_right == "가압류":
            score += 20
        elif "경매" in base_right:
            score += 10
        else:
            score += 30
            reasons.append("말소기준권리 확인 필요")

        tenant = rights.get("tenant_priority", "")

        if tenant == "임차인 없음":
            pass
        elif "선순위" in tenant:
            score += 40
            reasons.append("선순위 임차인")
        elif "후순위" in tenant:
            score += 10
        elif "대항력" in tenant:
            score += 35
            reasons.append("대항력 가능성")
        else:
            score += 15
            reasons.append("임차인 권리관계 확인 필요")

        occupancy = rights.get("occupancy", "")

        if occupancy == "소유자 점유":
            pass
        elif occupancy == "공실":
            score += 5
        elif occupancy == "임차인 점유":
            score += 15
            reasons.append("임차인 점유")
        else:
            score += 10
            reasons.append("점유관계 확인 필요")

        takeover = rights.get("takeover_amount", 0)

        if takeover > 300000000:
            score += 40
            reasons.append("인수금 매우 큼")
        elif takeover > 100000000:
            score += 20
            reasons.append("인수금 발생")
        elif takeover > 0:
            score += 10
            reasons.append("소액 인수금 발생")

        confidence = rights.get("confidence", 0)

        if confidence < 70:
            score += 20
            reasons.append("AI 신뢰도 낮음")
        elif confidence < 90:
            score += 5

        legal = rights.get("legal", {})

        surface = legal.get("statutory_surface_right")

        if surface and surface.get("exists"):
            score += surface.get("risk", 60)
            reasons.append("법정지상권 가능성")

        if score < 20:
            risk = "LOW"
        elif score < 50:
            risk = "MEDIUM"
        elif score < 80:
            risk = "HIGH"
        else:
            risk = "VERY_HIGH"

        return {
            "version": self.VERSION,
            "risk_score": score,
            "risk_level": risk,
            "reasons": reasons,
        }


rights_risk_engine = RightsRiskEngine()
