import re
from typing import Dict, Tuple


class DepositAnalyzer:
    """
    MCP16 Deposit Analyzer

    OCR Text에서 보증금/임대차보증금/전세금/deposit 값을 추출합니다.
    """

    VERSION = "MCP16-DEPOSIT-1.1"

    def analyze(self, text: str) -> Dict:
        text = text or ""

        amount, source = self._extract_deposit(text)

        return {
            "version": self.VERSION,
            "lease_deposit": amount,
            "deposit_found": amount > 0,
            "source_text": source,
            "confidence": 90.0 if amount > 0 else 50.0,
            "reason": (
                f"보증금 {amount:,}원이 감지되었습니다."
                if amount > 0
                else "보증금 정보를 찾지 못했습니다."
            ),
        }

    def _extract_deposit(self, text: str) -> Tuple[int, str]:
        patterns = [
            r"(보증금|임대차보증금|전세금)\s*[:：]?\s*([0-9]+억[0-9]*천?만?원?)",
            r"(보증금|임대차보증금|전세금)\s*[:：]?\s*([0-9]+천만원)",
            r"(보증금|임대차보증금|전세금)\s*[:：]?\s*([0-9]+만원)",
            r"(보증금|임대차보증금|전세금)\s*[:：]?\s*([0-9,]+)\s*원?",
            r"deposit\s*[:：]?\s*([0-9,]+)",
            r"lease_deposit\s*[:：]?\s*([0-9,]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                source = match.group(0)
                amount_text = match.group(match.lastindex)
                amount = self._parse_amount(amount_text)

                if amount > 0:
                    return amount, source

        return 0, ""

    def _parse_amount(self, value: str) -> int:
        if not value:
            return 0

        value = value.replace(",", "")
        value = value.replace(" ", "")
        value = value.replace("원", "")

        if re.fullmatch(r"[0-9]+", value):
            return int(value)

        total = 0

        eok_match = re.search(r"([0-9]+)억", value)
        if eok_match:
            total += int(eok_match.group(1)) * 100_000_000

        after_eok = value.split("억")[-1] if "억" in value else value

        cheonman_match = re.search(r"([0-9]+)천만", after_eok)
        if cheonman_match:
            total += int(cheonman_match.group(1)) * 10_000_000

        man_match = re.search(r"([0-9]+)만", after_eok)
        if man_match and not cheonman_match:
            total += int(man_match.group(1)) * 10_000

        return total


deposit_analyzer = DepositAnalyzer()
