CREATE TABLE IF NOT EXISTS mcp4.short_loan_daily (
    trade_date DATE,
    stock_code VARCHAR(12),
    stock_name VARCHAR(200),

    short_amount BIGINT DEFAULT 0,
    short_ratio NUMERIC(8,2) DEFAULT 0,

    loan_balance BIGINT DEFAULT 0,
    loan_change BIGINT DEFAULT 0,

    short_score NUMERIC(8,2) DEFAULT 50,
    loan_score NUMERIC(8,2) DEFAULT 50,
    total_score NUMERIC(8,2) DEFAULT 50,

    memo TEXT,
    created_at TIMESTAMP DEFAULT NOW(),

    PRIMARY KEY (trade_date, stock_code)
);
