"""
MCP16 Rights Summary Engine V2

권리분석 결과를 사람이 읽기 쉬운 요약문으로 변환합니다.
"""


class RightsSummaryEngineV2:

    VERSION = "MCP16-RIGHTS-SUMMARY-2.0"

    def build(self, data: dict) -> dict:

        base_right = data.get("base_right", "미확인")
        tenant_priority = data.get("tenant_priority", "미확인")
        occupancy = data.get("occupancy", "미확인")
        takeover_amount = int(data.get("takeover_amount", 0) or 0)
        legal_risk_count = data.get("legal_risk_count", 0)
        risk_level = data.get("risk_level", "UNKNOWN")
        rights_score = data.get("rights_score", 0)

        lines = [
            f"말소기준권리는 {base_right}입니다.",
            f"임차인 권리상태는 {tenant_priority}입니다.",
            f"점유상태는 {occupancy}입니다.",
            f"예상 인수금액은 {takeover_amount:,}원입니다.",
        ]

        if legal_risk_count > 0:
            lines.append(f"법률 위험요소가 {legal_risk_count}건 감지되었습니다.")
        else:
            lines.append("특이 법률 위험요소는 감지되지 않았습니다.")

        lines.append(
            f"권리점수는 {rights_score}점이며 위험등급은 {risk_level}입니다."
        )

        return {
            "version": self.VERSION,
            "summary": " ".join(lines),
            "summary_lines": lines,
        }


rights_summary_engine_v2 = RightsSummaryEngineV2()
