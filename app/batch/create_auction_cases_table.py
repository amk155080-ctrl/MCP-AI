from sqlalchemy import text
from app.core.database import engine


def run():
    create_sql = """
    CREATE TABLE IF NOT EXISTS auction_cases (
        id SERIAL PRIMARY KEY,
        document_id INTEGER,
        auction_id INTEGER,

        case_no VARCHAR(100),
        court_name VARCHAR(100),
        property_address TEXT,
        property_type VARCHAR(100),

        appraisal_price BIGINT DEFAULT 0,
        minimum_bid_price BIGINT DEFAULT 0,
        expected_sale_price BIGINT DEFAULT 0,

        status VARCHAR(50) DEFAULT 'WATCH',
        memo TEXT,

        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """

    with engine.begin() as conn:
        conn.execute(text(create_sql))

    print("MCP19-001 auction_cases table created successfully")


if __name__ == "__main__":
    run()
