"""
MCP16 Rights Score Engine V2

권리분석 결과를 종합하여
권리점수와 위험등급을 계산합니다.
"""


class RightsScoreEngineV2:

    VERSION = "MCP16-RIGHTS-SCORE-2.0"

    def calculate(self, data: dict) -> dict:

        score = 100

        base_right = data.get("base_right", "")
        tenant_priority = data.get("tenant_priority", "")
        takeover_amount = data.get("takeover_amount", 0)
        legal_risk_score = data.get("legal_risk_score", 0)
        occupant_type = data.get("occupant_type", "")

        # 말소기준권리
        if base_right == "미확인":
            score -= 25

        # 임차인 위험
        if "선순위" in tenant_priority:
            score -= 30
        elif "대항력" in tenant_priority:
            score -= 25
        elif "미확인" in tenant_priority:
            score -= 15

        # 인수금액
        if takeover_amount > 0:
            score -= 30

        # 법률위험
        score -= min(legal_risk_score, 40)

        # 점유자
        if occupant_type == "TENANT":
            score -= 10
        elif occupant_type == "THIRD_PARTY":
            score -= 20
        elif occupant_type == "UNKNOWN":
            score -= 10

        score = max(0, min(score, 100))

        return {
            "version": self.VERSION,
            "rights_score": score,
            "risk_level": self._risk_level(score),
            "recommendation": self._recommendation(score),
        }

    def _risk_level(self, score: int):

        if score >= 90:
            return "LOW"

        if score >= 70:
            return "MEDIUM"

        if score >= 50:
            return "HIGH"

        return "VERY_HIGH"

    def _recommendation(self, score: int):

        if score >= 90:
            return "입찰 가능"

        if score >= 70:
            return "검토 후 입찰"

        if score >= 50:
            return "주의 필요"

        return "입찰 비추천"


rights_score_engine_v2 = RightsScoreEngineV2()
