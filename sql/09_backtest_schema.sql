CREATE TABLE IF NOT EXISTS mcp4.backtest_report (
    trade_date DATE,
    portfolio_type VARCHAR(50),

    initial_capital NUMERIC(20,2),
    final_capital NUMERIC(20,2),

    total_return NUMERIC(8,2),
    cagr NUMERIC(8,2),
    mdd NUMERIC(8,2),
    win_rate NUMERIC(8,2),
    sharpe NUMERIC(8,2),

    memo TEXT,
    created_at TIMESTAMP DEFAULT NOW(),

    PRIMARY KEY (trade_date, portfolio_type)
);
