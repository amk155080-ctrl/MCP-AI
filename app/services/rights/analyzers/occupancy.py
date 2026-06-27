import re
from typing import Dict


class OccupancyAnalyzer:
    """
    MCP16 Occupancy Analyzer

    점유자 유형을 분석한다.
    """

    VERSION = "MCP16-OCCUPANCY-1.0"

    def analyze(self, text: str) -> Dict:

        text = text or ""
        lower = text.lower()

        occupancy = self._detect(text, lower)

        return {
            "version": self.VERSION,
            "occupancy": occupancy["label"],
            "occupant_type": occupancy["type"],
            "risk": occupancy["risk"],
            "confidence": occupancy["confidence"],
            "reason": occupancy["reason"],
        }

    def _detect(self, text: str, lower: str):

        rules = [

            (
                [
                    "occupancy:owner",
                    "occupancy: owner",
                    "소유자 점유",
                ],
                "OWNER",
                "소유자 점유",
                5,
                95,
            ),

            (
                [
                    "occupancy:tenant",
                    "occupancy: tenant",
                    "임차인 점유",
                ],
                "TENANT",
                "임차인 점유",
                30,
                95,
            ),

            (
                [
                    "occupancy:debtor",
                    "occupancy: debtor",
                    "채무자 점유",
                ],
                "DEBTOR",
                "채무자 점유",
                15,
                90,
            ),

            (
                [
                    "occupancy:third",
                    "occupancy: third",
                    "제3자 점유",
                ],
                "THIRD_PARTY",
                "제3자 점유",
                40,
                90,
            ),

            (
                [
                    "공실",
                    "vacant",
                ],
                "VACANT",
                "공실",
                0,
                98,
            ),
        ]

        for keywords, code, label, risk, conf in rules:

            for keyword in keywords:

                if keyword.lower() in lower:

                    return {
                        "type": code,
                        "label": label,
                        "risk": risk,
                        "confidence": conf,
                        "reason": f"{label} 감지",
                    }

        return {
            "type": "UNKNOWN",
            "label": "점유자 미상",
            "risk": 20,
            "confidence": 50,
            "reason": "점유자 정보를 찾지 못했습니다.",
        }


occupancy_analyzer = OccupancyAnalyzer()