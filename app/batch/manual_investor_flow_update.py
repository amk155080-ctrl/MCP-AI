import argparse
from sqlalchemy import text
from app.core.database import SessionLocal


def run(trade_date):
    rows = [
        ("000660", 180000000000, 95000000000, 50000000000, 40000000000),
        ("042700", 75000000000, 62000000000, 25000000000, 18000000000),
        ("005930", 60000000000, 30000000000, 15000000000, 12000000000),
        ("095340", 25000000000, 18000000000, 8000000000, 6000000000),
        ("089030", 22000000000, 15000000000, 7000000000, 5000000000),
        ("039030", 15000000000, 10000000000, 5000000000, 4000000000),
    ]

    db = SessionLocal()

    try:
        for stock_code, foreign_net, institution_net, pension_net, program_net in rows:
            db.execute(
                text(
                    """
                    INSERT INTO mcp4.investor_flow_daily
                    (
                        trade_date,
                        stock_code,
                        foreign_net,
                        institution_net,
                        pension_net,
                        program_net
                    )
                    VALUES
                    (
                        :trade_date,
                        :stock_code,
                        :foreign_net,
                        :institution_net,
                        :pension_net,
                        :program_net
                    )
                    ON CONFLICT (trade_date, stock_code)
                    DO UPDATE SET
                        foreign_net = EXCLUDED.foreign_net,
                        institution_net = EXCLUDED.institution_net,
                        pension_net = EXCLUDED.pension_net,
                        program_net = EXCLUDED.program_net
                    """
                ),
                {
                    "trade_date": trade_date,
                    "stock_code": stock_code,
                    "foreign_net": foreign_net,
                    "institution_net": institution_net,
                    "pension_net": pension_net,
                    "program_net": program_net,
                },
            )

        db.commit()

    finally:
        db.close()

    print("[INVESTOR FLOW]", trade_date, "saved")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    run(args.date)
