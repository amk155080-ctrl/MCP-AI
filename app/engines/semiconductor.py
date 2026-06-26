def grade(score):
    if score >= 90:
        return "SS"
    if score >= 80:
        return "S"
    if score >= 70:
        return "A"
    if score >= 60:
        return "B"
    return "C"


def hbm_premium_score(stock_code):
    premium = {
        "000660": 35,  # SK하이닉스
        "042700": 33,  # 한미반도체
        "089030": 29,  # 테크윙
        "095340": 29,  # ISC
        "039030": 27,  # 이오테크닉스
        "005930": 26,  # 삼성전자
        "058470": 23,  # 리노공업
        "403870": 23,  # HPSP
    }

    return premium.get(stock_code, 15)


def calculate_semiconductor_score(row, market_score):
    sox_score = min(30, max(0, float(market_score) * 0.30))

    hbm_score = hbm_premium_score(row.stock_code)

    theme_bonus = 0

    if row.hbf_flag:
        theme_bonus += 5

    if row.cxl_flag:
        theme_bonus += 4

    if row.ai_server_flag:
        theme_bonus += 4

    if row.packaging_flag:
        theme_bonus += 4

    nvda_score = 10
    flow_score = 10
    earnings_score = 10

    total = min(
        100,
        round(
            sox_score +
            hbm_score +
            theme_bonus +
            nvda_score +
            flow_score +
            earnings_score,
            2,
        ),
    )

    return {
        "stock_code": row.stock_code,
        "stock_name": row.stock_name,
        "sox_score": round(sox_score, 2),
        "nvda_score": nvda_score,
        "hbm_score": round(hbm_score + theme_bonus, 2),
        "flow_score": flow_score,
        "earnings_score": earnings_score,
        "total_score": total,
        "grade": grade(total),
    }
