import argparse
from datetime import datetime
from sqlalchemy import text
from app.core.database import SessionLocal


def calc_weight(score, rank_no):
    if score >= 85:
        base = 25
    elif score >= 80:
        base = 20
    elif score >= 75:
        base = 15
    elif score >= 70:
        base = 10
    else:
        base = 5

    # 상위 종목 우대
    if rank_no == 1:
        base += 3
    elif rank_no == 2:
        base += 2
    elif rank_no == 3:
        base += 1

    return min(base, 30)


def normalize_weights(positions, max_total=90):
    total = sum(p["weight"] for p in positions)

    if total <= 0:
        return positions

    if total > max_total:
        for p in positions:
            p["weight"] = round(p["weight"] / total * max_total, 2)

    return positions


def build_ai_semiconductor(db, trade_date):
    rows = db.execute(
        text(
            """
            SELECT
                trade_date,
                stock_code,
                stock_name,
                total_score,
                signal
            FROM mcp4.institutional_score_daily
            WHERE trade_date = :trade_date
              AND total_score >= 70
            ORDER BY total_score DESC
            LIMIT 10
            """
        ),
        {"trade_date": trade_date},
    ).fetchall()

    positions = []

    for idx, r in enumerate(rows, start=1):
        weight = calc_weight(float(r.total_score), idx)

        positions.append(
            {
                "trade_date": trade_date,
                "portfolio_type": "AI_SEMICONDUCTOR",
                "stock_code": r.stock_code,
                "stock_name": r.stock_name,
                "total_score": float(r.total_score),
                "signal": r.signal,
                "weight": weight,
                "rank_no": idx,
                "memo": "AI 반도체 기관 점수 기반 자동 포트폴리오",
            }
        )

    return normalize_weights(positions)


def save_positions(db, positions):
    for p in positions:
        db.execute(
            text(
                """
                INSERT INTO mcp4.portfolio_position_daily
                (
                    trade_date,
                    portfolio_type,
                    stock_code,
                    stock_name,
                    total_score,
                    signal,
                    weight,
                    rank_no,
                    memo
                )
                VALUES
                (
                    :trade_date,
                    :portfolio_type,
                    :stock_code,
                    :stock_name,
                    :total_score,
                    :signal,
                    :weight,
                    :rank_no,
                    :memo
                )
                ON CONFLICT (trade_date, portfolio_type, stock_code)
                DO UPDATE SET
                    stock_name = EXCLUDED.stock_name,
                    total_score = EXCLUDED.total_score,
                    signal = EXCLUDED.signal,
                    weight = EXCLUDED.weight,
                    rank_no = EXCLUDED.rank_no,
                    memo = EXCLUDED.memo
                """
            ),
            p,
        )


def run(trade_date):
    db = SessionLocal()

    try:
        db.execute(
            text(
                """
                DELETE FROM mcp4.portfolio_position_daily
                WHERE trade_date = :trade_date
                  AND portfolio_type = 'AI_SEMICONDUCTOR'
                """
            ),
            {"trade_date": trade_date},
        )

        positions = build_ai_semiconductor(db, trade_date)

        save_positions(db, positions)

        db.commit()

    finally:
        db.close()

    print("[PORTFOLIO]", trade_date, "AI_SEMICONDUCTOR saved")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    args = parser.parse_args()
    run(args.date)
