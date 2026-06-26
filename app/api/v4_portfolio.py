from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(prefix="/api/v4/portfolio", tags=["portfolio-v4"])


def calc_weight(rank, total_score):
    total_score = float(total_score or 0)

    if rank == 1:
        return 25.0
    if rank == 2:
        return 20.0
    if rank == 3:
        return 18.0
    if rank == 4:
        return 15.0
    if rank == 5:
        return 12.0

    return 10.0


@router.get("/recommend")
def recommend_portfolio(
    capital: int = Query(10000000, description="투자금액"),
    limit: int = Query(5, description="추천 종목 수"),
):
    db = SessionLocal()

    try:
        rows = db.execute(text("""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,
                s.total_score,
                s.grade,
                p.close_price,
                p.trade_value,
                p.market_cap,
                COALESCE(f.foreign_net, 0) AS foreign_net,
                COALESCE(f.institution_net, 0) AS institution_net,
                COALESCE(f.pension_net, 0) AS pension_net,
                (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
                ) AS smart_money_net,
                CASE
                    WHEN s.total_score >= 80 THEN 'STRONG_BUY'
                    WHEN s.total_score >= 70 THEN 'BUY'
                    WHEN s.total_score >= 60 THEN 'WATCH'
                    ELSE 'AVOID'
                END AS signal
            FROM mcp4.stock_score_daily s
            JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code
            LEFT JOIN mcp4.investor_flow_daily f
              ON s.trade_date = f.trade_date
             AND s.stock_code = f.stock_code
            WHERE s.total_score >= 70
              AND p.market_cap >= 500000000000
              AND p.trade_value >= 30000000000
              AND (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
              ) >= 5000000000
            ORDER BY
                smart_money_net DESC,
                s.total_score DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        items = []
        used_weight = 0.0

        for idx, r in enumerate(rows, start=1):
            weight = calc_weight(idx, r["total_score"])
            used_weight += weight

            invest_amount = int(capital * weight / 100)
            close_price = float(r["close_price"] or 0)

            qty = int(invest_amount // close_price) if close_price > 0 else 0
            real_amount = int(qty * close_price)

            item = dict(r)
            item["rank"] = idx
            item["weight_percent"] = weight
            item["target_amount"] = invest_amount
            item["buy_quantity"] = qty
            item["estimated_buy_amount"] = real_amount

            items.append(item)

        cash_weight = max(0.0, 100.0 - used_weight)
        cash_amount = int(capital * cash_weight / 100)

        return {
            "capital": capital,
            "recommend_count": len(items),
            "cash_weight_percent": cash_weight,
            "cash_amount": cash_amount,
            "items": items,
        }

    finally:
        db.close()


@router.get("/risk_check")
def portfolio_risk_check(
    capital: int = Query(10000000, description="투자금액"),
    limit: int = Query(5, description="추천 종목 수"),
):
    db = SessionLocal()

    try:
        rows = db.execute(text("""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,
                s.total_score,
                s.risk_score,
                s.grade,
                p.close_price,
                p.trade_value,
                p.market_cap,
                COALESCE(f.foreign_net, 0) AS foreign_net,
                COALESCE(f.institution_net, 0) AS institution_net,
                COALESCE(f.pension_net, 0) AS pension_net,
                (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
                ) AS smart_money_net
            FROM mcp4.stock_score_daily s
            JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code
            LEFT JOIN mcp4.investor_flow_daily f
              ON s.trade_date = f.trade_date
             AND s.stock_code = f.stock_code
            WHERE s.total_score >= 70
              AND p.market_cap >= 500000000000
              AND p.trade_value >= 30000000000
              AND (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
              ) >= 5000000000
            ORDER BY
                smart_money_net DESC,
                s.total_score DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        items = []
        total_weight = 0.0
        weighted_score = 0.0
        weighted_risk = 0.0
        high_risk_count = 0

        for idx, r in enumerate(rows, start=1):
            weight = calc_weight(idx, r["total_score"])
            total_weight += weight

            total_score = float(r["total_score"] or 0)
            risk_score = float(r["risk_score"] or 0)
            market_cap = float(r["market_cap"] or 0)

            weighted_score += total_score * weight / 100
            weighted_risk += risk_score * weight / 100

            risk_level = "NORMAL"

            if risk_score < 50 or market_cap < 1000000000000:
                risk_level = "HIGH"
                high_risk_count += 1
            elif risk_score < 60:
                risk_level = "CAUTION"

            item = dict(r)
            item["rank"] = idx
            item["weight_percent"] = weight
            item["risk_level"] = risk_level
            items.append(item)

        cash_weight = max(0.0, 100.0 - total_weight)

        if high_risk_count >= 3:
            portfolio_risk = "HIGH_RISK"
        elif high_risk_count >= 1:
            portfolio_risk = "CAUTION"
        else:
            portfolio_risk = "NORMAL_RISK"

        if cash_weight >= 20:
            cash_comment = "현금 비중이 충분해 방어력이 있습니다."
        elif cash_weight >= 10:
            cash_comment = "현금 비중은 보통 수준입니다."
        else:
            cash_comment = "현금 비중이 낮아 변동성 확대 시 주의가 필요합니다."

        return {
            "capital": capital,
            "recommend_count": len(items),
            "cash_weight_percent": cash_weight,
            "cash_amount": int(capital * cash_weight / 100),
            "average_score": round(weighted_score, 2),
            "average_risk_score": round(weighted_risk, 2),
            "high_risk_count": high_risk_count,
            "portfolio_risk": portfolio_risk,
            "cash_comment": cash_comment,
            "items": items,
        }

    finally:
        db.close()


@router.get("/stable_recommend")
def stable_recommend_portfolio(
    capital: int = Query(10000000, description="투자금액"),
    limit: int = Query(5, description="추천 종목 수"),
):
    db = SessionLocal()

    try:
        rows = db.execute(text("""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,
                s.total_score,
                s.risk_score,
                s.grade,
                p.close_price,
                p.trade_value,
                p.market_cap,
                COALESCE(f.foreign_net, 0) AS foreign_net,
                COALESCE(f.institution_net, 0) AS institution_net,
                COALESCE(f.pension_net, 0) AS pension_net,
                (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
                ) AS smart_money_net,
                CASE
                    WHEN s.total_score >= 80 THEN 'STRONG_BUY'
                    WHEN s.total_score >= 70 THEN 'BUY'
                    WHEN s.total_score >= 60 THEN 'WATCH'
                    ELSE 'AVOID'
                END AS signal
            FROM mcp4.stock_score_daily s
            JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code
            LEFT JOIN mcp4.investor_flow_daily f
              ON s.trade_date = f.trade_date
             AND s.stock_code = f.stock_code
            WHERE s.total_score >= 65
              AND p.market_cap >= 1000000000000
              AND p.trade_value >= 30000000000
              AND (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
              ) >= 5000000000
            ORDER BY
                smart_money_net DESC,
                s.total_score DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        items = []
        used_weight = 0.0

        for idx, r in enumerate(rows, start=1):
            weight = calc_weight(idx, r["total_score"])
            used_weight += weight

            invest_amount = int(capital * weight / 100)
            close_price = float(r["close_price"] or 0)

            qty = int(invest_amount // close_price) if close_price > 0 else 0
            real_amount = int(qty * close_price)

            item = dict(r)
            item["rank"] = idx
            item["weight_percent"] = weight
            item["target_amount"] = invest_amount
            item["buy_quantity"] = qty
            item["estimated_buy_amount"] = real_amount
            item["risk_level"] = "NORMAL"

            items.append(item)

        cash_weight = max(0.0, 100.0 - used_weight)
        cash_amount = int(capital * cash_weight / 100)

        return {
            "capital": capital,
            "strategy": "STABLE_QUALITY",
            "recommend_count": len(items),
            "cash_weight_percent": cash_weight,
            "cash_amount": cash_amount,
            "items": items,
        }

    finally:
        db.close()


@router.get("/aggressive_recommend")
def aggressive_recommend_portfolio(
    capital: int = Query(10000000, description="투자금액"),
    limit: int = Query(5, description="추천 종목 수"),
):
    db = SessionLocal()

    try:
        rows = db.execute(text("""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,
                s.total_score,
                s.risk_score,
                s.grade,
                p.close_price,
                p.trade_value,
                p.market_cap,
                COALESCE(f.foreign_net, 0) AS foreign_net,
                COALESCE(f.institution_net, 0) AS institution_net,
                COALESCE(f.pension_net, 0) AS pension_net,
                (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
                ) AS smart_money_net,
                CASE
                    WHEN s.total_score >= 80 THEN 'STRONG_BUY'
                    WHEN s.total_score >= 70 THEN 'BUY'
                    WHEN s.total_score >= 60 THEN 'WATCH'
                    ELSE 'AVOID'
                END AS signal
            FROM mcp4.stock_score_daily s
            JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code
            LEFT JOIN mcp4.investor_flow_daily f
              ON s.trade_date = f.trade_date
             AND s.stock_code = f.stock_code
            WHERE s.total_score >= 70
              AND p.market_cap >= 100000000000
              AND p.trade_value >= 10000000000
              AND (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
              ) >= 2000000000
            ORDER BY
                s.total_score DESC,
                smart_money_net DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        items = []
        used_weight = 0.0

        for idx, r in enumerate(rows, start=1):
            weight = calc_weight(idx, r["total_score"])
            used_weight += weight

            invest_amount = int(capital * weight / 100)
            close_price = float(r["close_price"] or 0)

            qty = int(invest_amount // close_price) if close_price > 0 else 0
            real_amount = int(qty * close_price)

            risk_level = "NORMAL"
            if float(r["market_cap"] or 0) < 500000000000:
                risk_level = "HIGH"
            elif float(r["market_cap"] or 0) < 1000000000000:
                risk_level = "CAUTION"

            item = dict(r)
            item["rank"] = idx
            item["weight_percent"] = weight
            item["target_amount"] = invest_amount
            item["buy_quantity"] = qty
            item["estimated_buy_amount"] = real_amount
            item["risk_level"] = risk_level

            items.append(item)

        cash_weight = max(0.0, 100.0 - used_weight)
        cash_amount = int(capital * cash_weight / 100)

        return {
            "capital": capital,
            "strategy": "AGGRESSIVE_SMART_MONEY",
            "recommend_count": len(items),
            "cash_weight_percent": cash_weight,
            "cash_amount": cash_amount,
            "items": items,
        }

    finally:
        db.close()


def build_strategy_portfolio(db, strategy, capital, limit):
    if strategy == "stable":
        where_clause = """
            s.total_score >= 65
            AND p.market_cap >= 1000000000000
            AND p.trade_value >= 30000000000
            AND (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
            ) >= 5000000000
        """
    else:
        where_clause = """
            s.total_score >= 70
            AND p.market_cap >= 100000000000
            AND p.trade_value >= 10000000000
            AND (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
            ) >= 2000000000
        """

    rows = db.execute(text(f"""
        SELECT
            s.trade_date,
            s.stock_code,
            s.stock_name,
            s.total_score,
            s.risk_score,
            s.grade,
            p.close_price,
            p.trade_value,
            p.market_cap,
            COALESCE(f.foreign_net, 0) AS foreign_net,
            COALESCE(f.institution_net, 0) AS institution_net,
            COALESCE(f.pension_net, 0) AS pension_net,
            (
                COALESCE(f.foreign_net,0)
              + COALESCE(f.institution_net,0)
              + COALESCE(f.pension_net,0)
            ) AS smart_money_net,
            CASE
                WHEN s.total_score >= 80 THEN 'STRONG_BUY'
                WHEN s.total_score >= 70 THEN 'BUY'
                WHEN s.total_score >= 60 THEN 'WATCH'
                ELSE 'AVOID'
            END AS signal
        FROM mcp4.stock_score_daily s
        JOIN mcp4.stock_price_daily p
          ON s.trade_date = p.trade_date
         AND s.stock_code = p.stock_code
        LEFT JOIN mcp4.investor_flow_daily f
          ON s.trade_date = f.trade_date
         AND s.stock_code = f.stock_code
        WHERE {where_clause}
        ORDER BY
            smart_money_net DESC,
            s.total_score DESC
        LIMIT :limit
    """), {"limit": limit}).mappings().all()

    items = []
    used_weight = 0.0
    weighted_score = 0.0
    weighted_risk = 0.0
    high_risk_count = 0

    for idx, r in enumerate(rows, start=1):
        weight = calc_weight(idx, r["total_score"])
        used_weight += weight

        close_price = float(r["close_price"] or 0)
        invest_amount = int(capital * weight / 100)
        qty = int(invest_amount // close_price) if close_price > 0 else 0
        real_amount = int(qty * close_price)

        total_score = float(r["total_score"] or 0)
        risk_score = float(r["risk_score"] or 0)
        market_cap = float(r["market_cap"] or 0)

        weighted_score += total_score * weight / 100
        weighted_risk += risk_score * weight / 100

        risk_level = "NORMAL"
        if market_cap < 500000000000:
            risk_level = "HIGH"
            high_risk_count += 1
        elif market_cap < 1000000000000:
            risk_level = "CAUTION"
            high_risk_count += 1

        item = dict(r)
        item["rank"] = idx
        item["weight_percent"] = weight
        item["target_amount"] = invest_amount
        item["buy_quantity"] = qty
        item["estimated_buy_amount"] = real_amount
        item["risk_level"] = risk_level

        items.append(item)

    cash_weight = max(0.0, 100.0 - used_weight)

    return {
        "strategy": strategy.upper(),
        "recommend_count": len(items),
        "cash_weight_percent": cash_weight,
        "cash_amount": int(capital * cash_weight / 100),
        "average_score": round(weighted_score, 2),
        "average_risk_score": round(weighted_risk, 2),
        "high_risk_count": high_risk_count,
        "items": items,
    }


@router.get("/compare")
def compare_portfolios(
    capital: int = Query(10000000, description="투자금액"),
    limit: int = Query(5, description="추천 종목 수"),
):
    db = SessionLocal()

    try:
        stable = build_strategy_portfolio(db, "stable", capital, limit)
        aggressive = build_strategy_portfolio(db, "aggressive", capital, limit)

        if aggressive["high_risk_count"] >= 3:
            recommended = "STABLE"
            reason = "공격형 포트폴리오에 고위험 종목이 많아 안정형이 더 적합합니다."
        elif aggressive["average_score"] - stable["average_score"] >= 5:
            recommended = "AGGRESSIVE"
            reason = "공격형의 평균 점수가 안정형보다 충분히 높아 공격형이 유리합니다."
        else:
            recommended = "STABLE"
            reason = "점수 차이가 크지 않아 리스크가 낮은 안정형이 더 적합합니다."

        return {
            "capital": capital,
            "recommended_strategy": recommended,
            "reason": reason,
            "stable": stable,
            "aggressive": aggressive,
        }

    finally:
        db.close()
