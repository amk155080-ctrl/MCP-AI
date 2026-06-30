def build_decision_summary(result: dict) -> str:
    return (
        f"경매 종합점수는 {result.get('auction_score')}점입니다. "
        f"권리점수는 {result.get('rights_score')}점, "
        f"수익점수는 {result.get('profit_score')}점, "
        f"위험점수는 {result.get('risk_score')}점입니다. "
        f"추천 입찰가는 {result.get('recommended_bid'):,}원이며, "
        f"예상 수익은 {result.get('expected_profit'):,}원입니다. "
        f"예상 수익률은 {result.get('expected_roi')}%입니다. "
        f"최종 판단은 {result.get('decision')}입니다."
    )
