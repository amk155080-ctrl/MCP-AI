from typing import Dict, List


class LegalAnalyzer:
    VERSION = "MCP16-LEGAL-1.0"

    def analyze(self, text: str, context: Dict = None) -> Dict:
        text = text or ""

        checks = [
            self._check("STATUTORY_SURFACE_RIGHT", "법정지상권", text, ["법정지상권", "지상권", "statutory surface right"], 60),
            self._check("LIEN", "유치권", text, ["유치권", "유치권신고", "유치권 신고", "유치권 행사", "공사대금", "lien"], 70),
            self._check("PRELIMINARY_REGISTRATION", "예고등기", text, ["예고등기", "preliminary registration"], 90),
            self._check("PROVISIONAL_DISPOSITION", "가처분", text, ["가처분", "처분금지가처분", "provisional disposition"], 60),
            self._check("PROVISIONAL_REGISTRATION", "가등기", text, ["가등기", "소유권이전청구권가등기", "담보가등기", "provisional registration"], 50),
            self._check("CO_OWNERSHIP", "공유지분", text, ["공유지분", "지분매각", "공유자", "co-ownership", "shared ownership"], 40),
            self._check("SENIOR_LEASEHOLD", "선순위 전세권", text, ["선순위 전세권", "전세권설정", "전세권", "senior leasehold", "leasehold"], 50),
            self._check("DIVIDEND_DEADLINE", "배당요구종기", text, ["배당요구종기", "배당요구 종기", "배당요구기한", "distribution deadline", "dividend deadline"], 20),
        ]

        detected = [item for item in checks if item["exists"]]
        total_risk = sum(item["risk"] for item in detected)

        return {
            "version": self.VERSION,
            "legal_risks": detected,
            "legal_risk_count": len(detected),
            "legal_risk_score": min(total_risk, 100),
            "has_legal_risk": len(detected) > 0,
            "confidence": 90.0 if detected else 80.0,
            "reason": self._reason(detected),
        }

    def _check(self, code: str, label: str, text: str, keywords: List[str], risk: int) -> Dict:
        found = self._contains_any(text, keywords)

        return {
            "code": code,
            "label": label,
            "exists": bool(found),
            "reason": found,
            "risk": risk if found else 0,
        }

    def _contains_any(self, text: str, keywords: List[str]) -> str:
        lower = text.lower()

        for keyword in keywords:
            if keyword.lower() in lower:
                return keyword

        return ""

    def _reason(self, detected: List[Dict]) -> str:
        if not detected:
            return "법률 위험요소가 감지되지 않았습니다."

        labels = [item["label"] for item in detected]
        return "법률 위험요소 감지: " + ", ".join(labels)


legal_analyzer = LegalAnalyzer()
