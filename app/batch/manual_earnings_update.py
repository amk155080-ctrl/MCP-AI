import argparse
from sqlalchemy import text
from app.core.database import SessionLocal


def run(trade_date):
    rows = [
        ("000660", "SK하이닉스", 92, 95, 92, 88, "HBM 중심 실적 개선 가정"),
        ("042700", "한미반도체", 88, 90, 86, 84, "HBM 장비 수주 모멘텀 가정"),
        ("005930", "삼성전자", 78, 75, 72, 70, "메모리 회복 및 AI 수요 가정"),
        ("089030", "테크윙", 82, 84, 80, 78, "HBM 검사장비 성장 가정"),
        ("095340", "ISC", 80, 82, 78, 76, "AI 반도체 테스트 소켓 수요 가정"),
        ("039030", "이오테크닉스", 76, 78, 74, 72, "후공정 장비 수요 가정"),
    ]

    db = SessionLocal()

    try:
        for stock_code, stock_name, sales, op, eps, roe, memo in rows:
            total = round(
                sales * 0.25 +
                op * 0.35 +
                eps * 0.25 +
                roe * 0.15,
                2,
            )

            db.execute(
                text(
                    """
                    INSERT INTO mcp4.earnings_score_manual
                    (
                        trade_date,
                        stock_code,
                        stock_name,
                        sales_score,
                        op_score,
                        eps_score,
                        roe_score,
                        total_score,
                        memo
                    )
                    VALUES
                    (
                        :trade_date,
                        :stock_code,
                        :stock_name,
                        :sales_score,
                        :op_score,
                        :eps_score,
                        :roe_score,
                        :total_score,
                        :memo
                    )
                    ON CONFLICT (trade_date, stock_code)
                    DO UPDATE SET
                        stock_name = EXCLUDED.stock_name,
                        sales_score = EXCLUDED.sales_score,
                        op_score = EXCLUDED.op_score,
                        eps_score = EXCLUDED.eps_score,
                        roe_score = EXCLUDED.roe_score,
                        total_score = EXCLUDED.total_score,
                        memo = EXCLUDED.memo
                    """
                ),
                {
                    "trade_date": trade_date,
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "sales_score": sales,
                    "op_score": op,
                    "eps_score": eps,
                    "roe_score": roe,
                    "total_score": total,
                    "memo": memo,
                },
            )

        db.commit()

    finally:
        db.close()

    print("[EARNINGS MANUAL]", trade_date, "saved")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    run(args.date)
