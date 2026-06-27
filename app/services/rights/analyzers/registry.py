from typing import List

from app.services.rights.analyzers.base_right import BaseRightAnalyzer
from app.services.rights.analyzers.tenant import TenantAnalyzer
from app.services.rights.analyzers.occupancy import OccupancyAnalyzer
from app.services.rights.analyzers.deposit import DepositAnalyzer


class AnalyzerRegistry:
    """
    MCP16 Analyzer Registry

    Rights Engine에서 사용할 Analyzer 목록을 중앙 관리합니다.
    """

    VERSION = "MCP16-ANALYZER-REGISTRY-1.0"

    def __init__(self):
        self.analyzers = [
            BaseRightAnalyzer(),
            TenantAnalyzer(),
            OccupancyAnalyzer(),
        ]

    def get_analyzers(self) -> List:
        return self.analyzers

    def analyze_all(self, text: str) -> dict:
        results = {
            "version": self.VERSION,
            "analyzers": {},
        }

        for analyzer in self.analyzers:
            name = analyzer.__class__.__name__
            results["analyzers"][name] = analyzer.analyze(text)

        return results


analyzer_registry = AnalyzerRegistry()