CREATE TABLE IF NOT EXISTS mcp4.flow_score_manual (
    trade_date DATE,
    stock_code VARCHAR(12),
    stock_name VARCHAR(200),
    foreign_score NUMERIC(8,2) DEFAULT 50,
    institution_score NUMERIC(8,2) DEFAULT 50,
    program_score NUMERIC(8,2) DEFAULT 50,
    total_score NUMERIC(8,2) DEFAULT 50,
    memo TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (trade_date, stock_code)
);
