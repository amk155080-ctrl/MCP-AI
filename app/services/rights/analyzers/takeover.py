from typing import Dict


class TakeoverAnalyzer:
    """
    MCP16 Takeover Calculator

    임차인 권리상태와 보증금을 기준으로 예상 인수금액을 계산합니다.
    """

    VERSION = "MCP16-TAKEOVER-1.0"

    def analyze(self, text: str, context: Dict = None) -> Dict:
        context = context or {}

        tenant_result = context.get("TenantAnalyzer", {})
        deposit_result = context.get("DepositAnalyzer", {})

        tenant_priority = tenant_result.get("tenant_priority", "임차인 미확인")
        lease_deposit = int(deposit_result.get("lease_deposit", 0) or 0)

        takeover_required = False
        takeover_amount = 0
        risk_flag = "NONE"

        if tenant_priority == "임차인 없음":
            reason = "임차인이 없어 인수금액이 없습니다."

        elif "선순위" in tenant_priority:
            takeover_required = lease_deposit > 0
            takeover_amount = lease_deposit
            risk_flag = "SENIOR_TENANT"
            reason = "선순위 임차인 가능성이 있어 보증금 인수 가능성이 있습니다."

        elif "대항력" in tenant_priority:
            takeover_required = lease_deposit > 0
            takeover_amount = lease_deposit
            risk_flag = "OPPOSING_POWER"
            reason = "대항력 가능성이 있어 보증금 인수 검토가 필요합니다."

        elif "후순위" in tenant_priority:
            reason = "후순위 임차인으로 1차 계산상 인수금액은 없습니다."

        else:
            risk_flag = "UNKNOWN_TENANT"
            reason = "임차인 권리상태가 불명확하여 추가 검토가 필요합니다."

        return {
            "version": self.VERSION,
            "takeover_amount": takeover_amount,
            "takeover_required": takeover_required,
            "tenant_priority": tenant_priority,
            "lease_deposit": lease_deposit,
            "risk_flag": risk_flag,
            "confidence": self._confidence(tenant_priority, lease_deposit),
            "reason": reason,
        }

    def _confidence(self, tenant_priority: str, lease_deposit: int) -> float:
        if tenant_priority == "임차인 없음":
            return 90.0

        if lease_deposit <= 0 and tenant_priority != "임차인 없음":
            return 60.0

        if "선순위" in tenant_priority or "대항력" in tenant_priority:
            return 85.0

        if "후순위" in tenant_priority:
            return 80.0

        return 50.0


takeover_analyzer = TakeoverAnalyzer()
