import re
from typing import Dict


class TenantAnalyzer:
    """
    MCP16 Tenant Analyzer

    OCR Text에서 임차인 존재 여부, 선순위/후순위 가능성,
    전입/확정일자/배당요구 여부를 분석합니다.
    """

    VERSION = "MCP16-TENANT-1.0"

    def analyze(self, text: str) -> Dict:
        text = text or ""
        lower_text = text.lower()

        tenant_priority = self._detect_tenant_priority(text, lower_text)

        return {
            "version": self.VERSION,
            "tenant_priority": tenant_priority,
            "has_tenant": self._has_tenant(text, lower_text),
            "move_in": self._has_move_in(text),
            "fixed_date": self._has_fixed_date(text),
            "distribution_request": self._has_distribution_request(text),
            "confidence": self._confidence(tenant_priority),
            "reason": self._reason(tenant_priority),
        }

    def _detect_tenant_priority(self, text: str, lower_text: str) -> str:
        if re.search(r"tenant_priority\s*:\s*none", lower_text):
            return "임차인 없음"

        if re.search(r"tenant_priority\s*:\s*senior", lower_text):
            return "선순위 임차인 가능성 있음"

        if re.search(r"tenant_priority\s*:\s*junior", lower_text):
            return "후순위 임차인 가능성 있음"

        if re.search(r"tenant_priority\s*:\s*unknown", lower_text):
            return "임차인 권리 미확인"

        if not self._has_tenant(text, lower_text):
            return "임차인 미확인"

        has_move_in = self._has_move_in(text)
        has_fixed_date = self._has_fixed_date(text)
        has_distribution = self._has_distribution_request(text)

        if has_move_in and has_fixed_date and has_distribution:
            return "대항력 및 우선변제 가능성 있음"

        if has_move_in and has_fixed_date:
            return "대항력 가능성 있음"

        if has_move_in:
            return "대항력 검토 필요"

        if "임차인" in text or "보증금" in text:
            return "임차인 있음 / 대항력 미확인"

        return "임차인 미확인"

    def _has_tenant(self, text: str, lower_text: str) -> bool:
        english_keywords = [
            "tenant",
            "tenant_priority",
            "lease",
            "deposit",
        ]

        korean_keywords = [
            "임차인",
            "세입자",
            "전입",
            "확정일자",
            "배당요구",
            "임대차",
            "보증금",
        ]

        for keyword in english_keywords:
            if keyword in lower_text:
                return True

        for keyword in korean_keywords:
            if keyword in text:
                return True

        return False

    def _has_move_in(self, text: str) -> bool:
        keywords = [
            "전입",
            "전입신고",
            "주민등록",
            "move in",
            "move-in",
        ]

        lower_text = text.lower()

        for keyword in keywords:
            if keyword.lower() in lower_text:
                return True

        return False

    def _has_fixed_date(self, text: str) -> bool:
        keywords = [
            "확정일자",
            "fixed date",
        ]

        lower_text = text.lower()

        for keyword in keywords:
            if keyword.lower() in lower_text:
                return True

        return False

    def _has_distribution_request(self, text: str) -> bool:
        keywords = [
            "배당요구",
            "배당 요구",
            "distribution request",
            "dividend request",
        ]

        lower_text = text.lower()

        for keyword in keywords:
            if keyword.lower() in lower_text:
                return True

        return False

    def _confidence(self, tenant_priority: str) -> float:
        if tenant_priority == "임차인 없음":
            return 90.0

        if tenant_priority in [
            "선순위 임차인 가능성 있음",
            "후순위 임차인 가능성 있음",
            "대항력 및 우선변제 가능성 있음",
            "대항력 가능성 있음",
        ]:
            return 85.0

        if tenant_priority == "대항력 검토 필요":
            return 75.0

        if tenant_priority == "임차인 있음 / 대항력 미확인":
            return 70.0

        return 50.0

    def _reason(self, tenant_priority: str) -> str:
        if tenant_priority == "임차인 없음":
            return "OCR Text에서 임차인 없음으로 판단되었습니다."

        if "선순위" in tenant_priority:
            return "선순위 임차인 가능성이 감지되었습니다."

        if "후순위" in tenant_priority:
            return "후순위 임차인 가능성이 감지되었습니다."

        if "대항력" in tenant_priority:
            return "전입, 확정일자, 배당요구 정보를 기준으로 대항력 검토가 필요합니다."

        if tenant_priority == "임차인 있음 / 대항력 미확인":
            return "임차인 또는 보증금 문구는 있으나 대항력 판단 정보가 부족합니다."

        return "임차인 관련 정보를 충분히 확인하지 못했습니다."


tenant_analyzer = TenantAnalyzer()
