class AssetHealthService:

    @staticmethod
    def evaluate(allocation: dict):
        score = 100
        comments = []

        cash_ratio = allocation.get("cash_ratio", 0)
        stock_ratio = allocation.get("stock_ratio", 0)
        etf_ratio = allocation.get("etf_ratio", 0)
        usd_ratio = allocation.get("usd_ratio", 0)
        bond_ratio = allocation.get("bond_ratio", 0)

        if cash_ratio < 10:
            score -= 15
            comments.append("현금 비중이 낮아 급락장 대응력이 약합니다.")
        elif cash_ratio > 40:
            score -= 5
            comments.append("현금 비중이 높아 수익 기회가 줄어들 수 있습니다.")
        else:
            comments.append("현금 비중은 적절합니다.")

        if stock_ratio > 70:
            score -= 20
            comments.append("주식 비중이 높아 변동성 위험이 큽니다.")
        elif stock_ratio < 20:
            score -= 5
            comments.append("주식 비중이 낮아 성장성이 부족할 수 있습니다.")
        else:
            comments.append("주식 비중은 양호합니다.")

        if etf_ratio >= 10:
            comments.append("ETF 분산 효과가 있습니다.")
        else:
            score -= 5
            comments.append("ETF 비중이 낮아 분산 효과가 부족합니다.")

        if usd_ratio >= 5:
            comments.append("달러 자산이 있어 환율 방어 효과가 있습니다.")
        else:
            score -= 5
            comments.append("달러 자산 비중이 낮습니다.")

        if bond_ratio >= 5:
            comments.append("채권 자산이 있어 방어력이 있습니다.")
        else:
            score -= 5
            comments.append("채권 비중이 낮아 안정성이 부족합니다.")

        if score >= 85:
            grade = "A"
            risk = "LOW"
        elif score >= 70:
            grade = "B"
            risk = "NORMAL"
        elif score >= 55:
            grade = "C"
            risk = "HIGH"
        else:
            grade = "D"
            risk = "VERY_HIGH"

        return {
            "version": "MCP 14.0",
            "score": score,
            "grade": grade,
            "risk_level": risk,
            "comments": comments,
            "message": "자산건전성 평가 완료",
        }
