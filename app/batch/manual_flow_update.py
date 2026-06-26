import argparse
from sqlalchemy import text
from app.core.database import SessionLocal


def run(trade_date):
    rows = [
        ("000660", "SK하이닉스", 85, 82, 75, "HBM 핵심, 외국인/기관 우호 가정"),
        ("005930", "삼성전자", 70, 68, 65, "대형주 수급 안정 가정"),
        ("042700", "한미반도체", 82, 80, 72, "HBM 장비 핵심 가정"),
        ("089030", "테크윙", 75, 72, 68, "HBM 검사 장비 수혜 가정"),
        ("095340", "ISC", 76, 74, 68, "AI 반도체 테스트 소켓 수혜 가정"),
        ("039030", "이오테크닉스", 72, 70, 65, "레이저 장비 수혜 가정"),
    ]

    db = SessionLocal()

    try:
        for stock_code, stock_name, foreign_score, institution_score, program_score, memo in rows:
            total_score = round(
                foreign_score * 0.45 +
                institution_score * 0.45 +
                program_score * 0.10,
                2,
            )

            db.execute(
                text(
                    """
                    INSERT INTO mcp4.flow_score_manual
                    (
                        trade_date,
                        stock_code,
                        stock_name,
                        foreign_score,
                        institution_score,
                        program_score,
                        total_score,
                        memo
                    )
                    VALUES
                    (
                        :trade_date,
                        :stock_code,
                        :stock_name,
                        :foreign_score,
                        :institution_score,
                        :program_score,
                        :total_score,
                        :memo
                    )
                    ON CONFLICT (trade_date, stock_code)
                    DO UPDATE SET
                        stock_name = EXCLUDED.stock_name,
                        foreign_score = EXCLUDED.foreign_score,
                        institution_score = EXCLUDED.institution_score,
                        program_score = EXCLUDED.program_score,
                        total_score = EXCLUDED.total_score,
                        memo = EXCLUDED.memo
                    """
                ),
                {
                    "trade_date": trade_date,
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "foreign_score": foreign_score,
                    "institution_score": institution_score,
                    "program_score": program_score,
                    "total_score": total_score,
                    "memo": memo,
                },
            )

        db.commit()

    finally:
        db.close()

    print("[FLOW MANUAL]", trade_date, "saved")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    run(args.date)
