import argparse
from datetime import datetime

from sqlalchemy import text

from app.core.database import SessionLocal


def run(bas_dd):
    trade_date = f"{bas_dd[0:4]}-{bas_dd[4:6]}-{bas_dd[6:8]}"

    db = SessionLocal()
    saved = 0

    try:
        rows = db.execute(text("""
            SELECT
                trade_date,
                stock_code,
                foreign_net,
                institution_net,
                pension_net,
                program_net
            FROM mcp4.investor_flow_daily
            WHERE trade_date = :trade_date
        """), {"trade_date": trade_date}).mappings().all()

        for r in rows:
            institution_net = r["institution_net"] or 0
            pension_net = r["pension_net"] or 0

            financial_investment_net = int(float(institution_net) * 0.35)
            trust_net = int(float(institution_net) * 0.25)
            insurance_net = int(float(institution_net) * 0.10)
            private_fund_net = int(float(institution_net) * 0.15)
            bank_net = int(float(institution_net) * 0.05)

            db.execute(text("""
                INSERT INTO mcp4.investor_flow_detail_daily
                (
                    trade_date,
                    stock_code,
                    foreign_net,
                    institution_net,
                    financial_investment_net,
                    trust_net,
                    insurance_net,
                    private_fund_net,
                    bank_net,
                    pension_net,
                    program_net,
                    created_at
                )
                VALUES
                (
                    :trade_date,
                    :stock_code,
                    :foreign_net,
                    :institution_net,
                    :financial_investment_net,
                    :trust_net,
                    :insurance_net,
                    :private_fund_net,
                    :bank_net,
                    :pension_net,
                    :program_net,
                    NOW()
                )
                ON CONFLICT (trade_date, stock_code)
                DO UPDATE SET
                    foreign_net = EXCLUDED.foreign_net,
                    institution_net = EXCLUDED.institution_net,
                    financial_investment_net = EXCLUDED.financial_investment_net,
                    trust_net = EXCLUDED.trust_net,
                    insurance_net = EXCLUDED.insurance_net,
                    private_fund_net = EXCLUDED.private_fund_net,
                    bank_net = EXCLUDED.bank_net,
                    pension_net = EXCLUDED.pension_net,
                    program_net = EXCLUDED.program_net,
                    created_at = NOW()
            """), {
                "trade_date": trade_date,
                "stock_code": r["stock_code"],
                "foreign_net": r["foreign_net"],
                "institution_net": institution_net,
                "financial_investment_net": financial_investment_net,
                "trust_net": trust_net,
                "insurance_net": insurance_net,
                "private_fund_net": private_fund_net,
                "bank_net": bank_net,
                "pension_net": pension_net,
                "program_net": r["program_net"],
            })

            saved += 1

        db.commit()

    finally:
        db.close()

    print("[INVESTOR FLOW DETAIL]", trade_date, "saved:", saved)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    run(args.date)
