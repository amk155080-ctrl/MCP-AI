from sqlalchemy import text
from app.core.database import engine


def migrate():
    sql_list = [
        "ALTER TABLE mcp4.auction_rights ADD COLUMN IF NOT EXISTS document_id INTEGER;",
        "ALTER TABLE mcp4.auction_rights ADD COLUMN IF NOT EXISTS base_right VARCHAR(200);",
        "ALTER TABLE mcp4.auction_rights ADD COLUMN IF NOT EXISTS tenant_priority VARCHAR(100);",
        "ALTER TABLE mcp4.auction_rights ADD COLUMN IF NOT EXISTS occupancy VARCHAR(100);",
        "ALTER TABLE mcp4.auction_rights ADD COLUMN IF NOT EXISTS lease_deposit FLOAT;",
        "ALTER TABLE mcp4.auction_rights ADD COLUMN IF NOT EXISTS takeover_amount FLOAT;",
        "ALTER TABLE mcp4.auction_rights ADD COLUMN IF NOT EXISTS confidence FLOAT;",
        "ALTER TABLE mcp4.auction_rights ADD COLUMN IF NOT EXISTS parser_version VARCHAR(50);",
        "ALTER TABLE mcp4.auction_rights ADD COLUMN IF NOT EXISTS raw_summary TEXT;",
        "ALTER TABLE mcp4.auction_rights ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();",
        "ALTER TABLE mcp4.auction_rights ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();",
        "CREATE INDEX IF NOT EXISTS idx_auction_rights_document_id ON mcp4.auction_rights(document_id);",
    ]

    with engine.begin() as conn:
        for sql in sql_list:
            conn.execute(text(sql))

    print("=" * 60)
    print("MCP16.3 auction_rights migration completed")
    print("=" * 60)


if __name__ == "__main__":
    migrate()
