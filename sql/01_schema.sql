CREATE SCHEMA IF NOT EXISTS mcp4;

CREATE TABLE IF NOT EXISTS mcp4.stock_master (
    stock_code VARCHAR(20) PRIMARY KEY,
    stock_name VARCHAR(120) NOT NULL,
    market_type VARCHAR(30),
    sector_name VARCHAR(120),
    listing_date DATE,
    listing_shares BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mcp4.stock_price_daily (
    trade_date DATE NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(120),
    open_price NUMERIC(20,2),
    high_price NUMERIC(20,2),
    low_price NUMERIC(20,2),
    close_price NUMERIC(20,2),
    change_amount NUMERIC(20,2),
    change_rate NUMERIC(10,4),
    volume BIGINT,
    trade_value NUMERIC(30,0),
    market_cap NUMERIC(30,0),
    listed_shares BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (trade_date, stock_code)
);

CREATE TABLE IF NOT EXISTS mcp4.market_index_daily (
    trade_date DATE NOT NULL,
    index_code VARCHAR(50) NOT NULL,
    index_name VARCHAR(120),
    close_price NUMERIC(20,4),
    change_amount NUMERIC(20,4),
    change_rate NUMERIC(10,4),
    volume NUMERIC(30,0),
    trade_value NUMERIC(30,0),
    market_cap NUMERIC(30,0),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (trade_date, index_code, index_name)
);

CREATE TABLE IF NOT EXISTS mcp4.global_macro_daily (
    trade_date DATE NOT NULL,
    indicator_code VARCHAR(50) NOT NULL,
    indicator_name VARCHAR(120),
    close_value NUMERIC(20,6),
    change_rate NUMERIC(10,4),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (trade_date, indicator_code)
);

CREATE TABLE IF NOT EXISTS mcp4.investor_flow_daily (
    trade_date DATE NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    foreign_net NUMERIC(30,0) DEFAULT 0,
    institution_net NUMERIC(30,0) DEFAULT 0,
    pension_net NUMERIC(30,0) DEFAULT 0,
    program_net NUMERIC(30,0) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (trade_date, stock_code)
);

CREATE TABLE IF NOT EXISTS mcp4.short_selling_daily (
    trade_date DATE NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    short_volume BIGINT,
    short_value NUMERIC(30,0),
    short_ratio NUMERIC(10,4),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (trade_date, stock_code)
);

CREATE TABLE IF NOT EXISTS mcp4.lending_balance_daily (
    trade_date DATE NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    lending_shares BIGINT,
    lending_amount NUMERIC(30,0),
    lending_change BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (trade_date, stock_code)
);

CREATE TABLE IF NOT EXISTS mcp4.stock_score_daily (
    trade_date DATE NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(120),
    supply_score NUMERIC(6,2) DEFAULT 0,
    momentum_score NUMERIC(6,2) DEFAULT 0,
    macro_score NUMERIC(6,2) DEFAULT 0,
    semiconductor_score NUMERIC(6,2) DEFAULT 0,
    risk_score NUMERIC(6,2) DEFAULT 0,
    total_score NUMERIC(6,2) DEFAULT 0,
    grade VARCHAR(30),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (trade_date, stock_code)
);

CREATE INDEX IF NOT EXISTS idx_price_date ON mcp4.stock_price_daily(trade_date);
CREATE INDEX IF NOT EXISTS idx_price_code_date ON mcp4.stock_price_daily(stock_code, trade_date DESC);
CREATE INDEX IF NOT EXISTS idx_score_date_score ON mcp4.stock_score_daily(trade_date, total_score DESC);
