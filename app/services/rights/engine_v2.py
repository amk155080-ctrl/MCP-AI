from app.services.rights.analyzers.registry import analyzer_registry
from app.services.rights.score_v2 import rights_score_engine_v2
from app.services.rights.summary_v2 import rights_summary_engine_v2


class RightsEngineV2:
    """
    MCP16 Rights Engine V2

    Registry → Score → Summary를 통합하는 엔진
    """

    VERSION = "MCP16-RIGHTS-ENGINE-2.0"

    def analyze(self, text: str) -> dict:
        registry_result = analyzer_registry.analyze_all(text)
        analyzers = registry_result.get("analyzers", {})

        base = analyzers.get("BaseRightAnalyzer", {})
        tenant = analyzers.get("TenantAnalyzer", {})
        occupancy = analyzers.get("OccupancyAnalyzer", {})
        deposit = analyzers.get("DepositAnalyzer", {})
        takeover = analyzers.get("TakeoverAnalyzer", {})
        legal = analyzers.get("LegalAnalyzer", {})

        # -----------------------------
        # 기본 분석 결과
        # -----------------------------
        data = {
            "version": self.VERSION,
            "base_right": base.get("base_right", "미확인"),
            "tenant_priority": tenant.get("tenant_priority", "임차인 미확인"),
            "occupancy": occupancy.get("occupancy", "미확인"),
            "occupant_type": occupancy.get("occupant_type", "UNKNOWN"),
            "lease_deposit": deposit.get("lease_deposit", 0),
            "takeover_amount": takeover.get("takeover_amount", 0),
            "takeover_required": takeover.get("takeover_required", False),
            "legal_risks": legal.get("legal_risks", []),
            "legal_risk_count": legal.get("legal_risk_count", 0),
            "legal_risk_score": legal.get("legal_risk_score", 0),
            "raw_analyzers": analyzers,
        }

        # -----------------------------
        # 권리 점수 계산
        # -----------------------------
        score_result = rights_score_engine_v2.calculate(data)

        data["rights_score"] = score_result["rights_score"]
        data["risk_level"] = score_result["risk_level"]
        data["recommendation"] = score_result["recommendation"]
        data["score_version"] = score_result["version"]

        # -----------------------------
        # 요약 생성
        # -----------------------------
        summary_result = rights_summary_engine_v2.build(data)

        data["summary"] = summary_result["summary"]
        data["summary_lines"] = summary_result["summary_lines"]
        data["summary_version"] = summary_result["version"]

        return data


rights_engine_v2 = RightsEngineV2()
