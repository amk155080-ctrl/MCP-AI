from typing import Dict

from app.services.rights_parser import parse_rights_from_text
from app.services.legal_checks import detect_statutory_surface_right


class RightsEngine:

    VERSION = "MCP16.4"

    def analyze(self, ocr_text: str) -> Dict:

        parsed = parse_rights_from_text(ocr_text)

        legal = {
            "statutory_surface_right": detect_statutory_surface_right(ocr_text)
        }

        result = {
            "version": self.VERSION,
            "base_right": parsed["base_right"],
            "tenant_priority": parsed["tenant_priority"],
            "occupancy": parsed["occupancy"],
            "lease_deposit": parsed["lease_deposit"],
            "takeover_amount": parsed["takeover_amount"],
            "confidence": parsed["confidence"],
            "parser_version": parsed["parser_version"],
            "raw_summary": parsed["raw_summary"],
            "legal": legal,
        }

        return result


rights_engine = RightsEngine()
