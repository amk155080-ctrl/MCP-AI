"""
MCP16 Rights Summary Engine

권리분석 결과를 사람이 읽기 쉬운 요약 문장으로 변환하는 모듈.
향후 MCP16.6에서 고도화 예정.
"""


def build_rights_summary(rights: dict, risk: dict = None) -> str:
    risk = risk or {}

    base_right = rights.get("base_right", "미확인")
    tenant_priority = rights.get("tenant_priority", "미확인")
    occupancy = rights.get("occupancy", "미확인")
    takeover_amount = rights.get("takeover_amount", 0)
    risk_level = risk.get("risk_level", "UNKNOWN")

    return (
        f"말소기준권리: {base_right}, "
        f"임차인 권리상태: {tenant_priority}, "
        f"점유상태: {occupancy}, "
        f"예상 인수금액: {int(takeover_amount):,}원, "
        f"법률 위험도: {risk_level}"
    )
