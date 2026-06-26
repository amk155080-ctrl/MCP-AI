CREATE TABLE IF NOT EXISTS mcp4.earnings_score_manual (
    trade_date DATE,
    stock_code VARCHAR(12),
    stock_name VARCHAR(200),
    sales_score NUMERIC(8,2) DEFAULT 50,
    op_score NUMERIC(8,2) DEFAULT 50,
    eps_score NUMERIC(8,2) DEFAULT 50,
    roe_score NUMERIC(8,2) DEFAULT 50,
    total_score NUMERIC(8,2) DEFAULT 50,
    memo TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (trade_date, stock_code)
);
