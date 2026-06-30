from typing import List

from app.services.rights.analyzers.base_right import BaseRightAnalyzer
from app.services.rights.analyzers.tenant import TenantAnalyzer
from app.services.rights.analyzers.occupancy import OccupancyAnalyzer
from app.services.rights.analyzers.deposit import DepositAnalyzer
from app.services.rights.analyzers.takeover import TakeoverAnalyzer
from app.services.rights.analyzers.legal import LegalAnalyzer


class AnalyzerRegistry:
    """
    MCP16 Analyzer Registry

    Rights Engine에서 사용할 Analyzer 목록을 중앙 관리합니다.
    순차 실행 결과를 context로 다음 Analyzer에 전달합니다.
    """

    VERSION = "MCP16-ANALYZER-REGISTRY-1.2"

    def __init__(self):
        self.analyzers = [
            BaseRightAnalyzer(),
            TenantAnalyzer(),
            OccupancyAnalyzer(),
            DepositAnalyzer(),
            TakeoverAnalyzer(),
            LegalAnalyzer(),
        ]

    def get_analyzers(self) -> List:
        return self.analyzers

    def analyze_all(self, text: str) -> dict:
        results = {
            "version": self.VERSION,
            "analyzers": {},
        }

        context = {}

        for analyzer in self.analyzers:
            name = analyzer.__class__.__name__

            try:
                result = analyzer.analyze(
                    text=text,
                    context=context,
                )
            except TypeError:
                result = analyzer.analyze(text)

            results["analyzers"][name] = result
            context[name] = result

        return results


analyzer_registry = AnalyzerRegistry()
