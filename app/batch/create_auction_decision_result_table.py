from sqlalchemy import text
from app.core.database import engine


def run():
    create_sql = """
    CREATE TABLE IF NOT EXISTS auction_decision_results (
        id SERIAL PRIMARY KEY,
        document_id INTEGER,
        auction_id INTEGER,
        rights_result_id INTEGER,

        version VARCHAR(80),
        appraisal_price BIGINT,
        minimum_bid_price BIGINT,
        expected_sale_price BIGINT,
        rights_score INTEGER,
        takeover_amount BIGINT,

        recommended_bid BIGINT,
        safe_bid_by_roi BIGINT,
        safe_bid_by_rights BIGINT,
        bid_to_appraisal_rate FLOAT,
        target_roi FLOAT,

        total_cost BIGINT,
        expected_profit BIGINT,
        expected_roi FLOAT,

        profit_score INTEGER,
        risk_score INTEGER,
        auction_score INTEGER,
        decision VARCHAR(50),
        confidence INTEGER,

        summary TEXT,
        raw_result TEXT,

        created_at TIMESTAMP DEFAULT NOW()
    );
    """

    with engine.begin() as conn:
        conn.execute(text(create_sql))

    print("MCP17-004 auction_decision_results table created successfully")


if __name__ == "__main__":
    run()
