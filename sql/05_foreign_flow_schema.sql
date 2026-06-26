CREATE TABLE IF NOT EXISTS mcp4.investor_flow_daily (
    trade_date DATE,
    stock_code VARCHAR(12),
    stock_name VARCHAR(200),

    foreign_net_buy BIGINT DEFAULT 0,
    institution_net_buy BIGINT DEFAULT 0,
    individual_net_buy BIGINT DEFAULT 0,

    foreign_score NUMERIC(8,2) DEFAULT 50,
    institution_score NUMERIC(8,2) DEFAULT 50,
    individual_score NUMERIC(8,2) DEFAULT 50,

    total_score NUMERIC(8,2) DEFAULT 50,

    memo TEXT,
    created_at TIMESTAMP DEFAULT NOW(),

    PRIMARY KEY (trade_date, stock_code)
);
