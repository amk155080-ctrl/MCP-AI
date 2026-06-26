CREATE TABLE IF NOT EXISTS mcp4.portfolio_position_daily (
    trade_date DATE,
    portfolio_type VARCHAR(50),
    stock_code VARCHAR(12),
    stock_name VARCHAR(200),

    total_score NUMERIC(8,2),
    signal VARCHAR(30),

    weight NUMERIC(8,2),
    rank_no INTEGER,

    memo TEXT,
    created_at TIMESTAMP DEFAULT NOW(),

    PRIMARY KEY (trade_date, portfolio_type, stock_code)
);

CREATE INDEX IF NOT EXISTS idx_portfolio_position_daily_rank
ON mcp4.portfolio_position_daily(trade_date, portfolio_type, rank_no);
