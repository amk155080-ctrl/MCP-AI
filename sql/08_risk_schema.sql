CREATE TABLE IF NOT EXISTS mcp4.portfolio_risk_daily (
    trade_date DATE,
    portfolio_type VARCHAR(50),

    invested_weight NUMERIC(8,2),
    cash_weight NUMERIC(8,2),

    avg_score NUMERIC(8,2),
    avg_risk_score NUMERIC(8,2),

    portfolio_risk_grade VARCHAR(30),

    var95 NUMERIC(8,2),
    expected_drawdown NUMERIC(8,2),

    memo TEXT,
    created_at TIMESTAMP DEFAULT NOW(),

    PRIMARY KEY (trade_date, portfolio_type)
);
