from app.core.database import engine
from sqlalchemy import text


def run():
    create_sql = """
    CREATE TABLE IF NOT EXISTS rights_v2_results (
        id SERIAL PRIMARY KEY,
        document_id INTEGER NOT NULL,
        auction_id INTEGER,
        version VARCHAR(50),
        base_right VARCHAR(100),
        tenant_priority VARCHAR(100),
        occupancy VARCHAR(100),
        lease_deposit BIGINT DEFAULT 0,
        takeover_amount BIGINT DEFAULT 0,
        takeover_required BOOLEAN DEFAULT FALSE,
        legal_risks TEXT,
        legal_risk_count INTEGER DEFAULT 0,
        rights_score INTEGER,
        risk_level VARCHAR(30),
        recommendation VARCHAR(100),
        summary TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """

    with engine.begin() as conn:
        conn.execute(text(create_sql))

    print("MCP16-011 rights_v2_results table created successfully")


if __name__ == "__main__":
    run()
