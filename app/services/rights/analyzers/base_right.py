import re
from typing import Dict


class BaseRightAnalyzer:
    """
    MCP16 Base Right Analyzer

    OCR Text에서 말소기준권리 후보를 추출합니다.
    """

    VERSION = "MCP16-BASE-RIGHT-1.0"

    def analyze(self, text: str) -> Dict:
        text = text or ""
        lower_text = text.lower()

        base_right = self._detect_base_right(text, lower_text)

        return {
            "version": self.VERSION,
            "base_right": base_right,
            "confidence": self._confidence(base_right),
            "reason": self._reason(base_right),
        }

    def _detect_base_right(self, text: str, lower_text: str) -> str:
        if re.search(r"base_right\s*:\s*mortgage", lower_text):
            return "근저당"

        if "mortgage" in lower_text:
            return "근저당"

        if re.search(r"base_right\s*:\s*seizure", lower_text):
            return "압류"

        if re.search(r"base_right\s*:\s*provisional_seizure", lower_text):
            return "가압류"

        if re.search(r"base_right\s*:\s*auction_start", lower_text):
            return "경매개시결정"

        if "근저당권" in text or "근저당" in text:
            return "근저당"

        if "저당권" in text:
            return "저당권"

        if "가압류" in text:
            return "가압류"

        if "압류" in text:
            return "압류"

        if "담보가등기" in text:
            return "담보가등기"

        if "강제경매개시결정" in text:
            return "강제경매개시결정"

        if "임의경매개시결정" in text:
            return "임의경매개시결정"

        if "경매개시결정" in text:
            return "경매개시결정"

        return "미확인"

    def _confidence(self, base_right: str) -> float:
        if base_right == "미확인":
            return 50.0

        return 90.0

    def _reason(self, base_right: str) -> str:
        if base_right == "미확인":
            return "말소기준권리 후보를 확인하지 못했습니다."

        return f"{base_right} 항목이 OCR Text에서 감지되었습니다."


base_right_analyzer = BaseRightAnalyzer()
