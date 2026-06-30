def calculate_profit_score(expected_roi: float) -> int:
    if expected_roi >= 25:
        return 100
    if expected_roi >= 20:
        return 90
    if expected_roi >= 15:
        return 80
    if expected_roi >= 10:
        return 65
    if expected_roi >= 5:
        return 50
    if expected_roi >= 0:
        return 35
    return 10


def calculate_risk_score(
    rights_score: int,
    expected_roi: float,
    takeover_amount: int = 0,
) -> int:
    risk = 100 - rights_score

    if expected_roi < 10:
        risk += 15

    if expected_roi < 0:
        risk += 30

    if takeover_amount > 0:
        risk += min(30, takeover_amount // 10_000_000)

    return max(0, min(100, risk))


def calculate_auction_score(
    rights_score: int,
    profit_score: int,
    risk_score: int,
) -> int:
    score = (
        rights_score * 0.4
        + profit_score * 0.4
        + (100 - risk_score) * 0.2
    )

    return round(score)


def make_decision(
    auction_score: int,
    rights_score: int,
    expected_roi: float,
    risk_score: int,
) -> str:
    if rights_score < 60:
        return "HOLD"

    if expected_roi < 8:
        return "HOLD"

    if risk_score >= 70:
        return "HOLD"

    if auction_score >= 80:
        return "BID"

    if auction_score >= 65:
        return "CAUTION_BID"

    return "HOLD"


def calculate_confidence(
    auction_score: int,
    rights_score: int,
    profit_score: int,
) -> int:
    confidence = int((auction_score + rights_score + profit_score) / 3)
    return max(0, min(100, confidence))
