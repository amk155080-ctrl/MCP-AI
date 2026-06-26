CREATE SCHEMA IF NOT EXISTS mcp4;

CREATE TABLE IF NOT EXISTS mcp4.macro_daily (
    trade_date DATE PRIMARY KEY,
    sox NUMERIC(12,2), nasdaq NUMERIC(12,2), sp500 NUMERIC(12,2),
    vix NUMERIC(12,2), us10y NUMERIC(12,4), dxy NUMERIC(12,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mcp4.market_regime_daily (
    trade_date DATE PRIMARY KEY,
    sox_score NUMERIC(8,2), vix_score NUMERIC(8,2), us10y_score NUMERIC(8,2),
    dxy_score NUMERIC(8,2), liquidity_score NUMERIC(8,2),
    total_score NUMERIC(8,2), regime VARCHAR(30),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mcp4.semiconductor_universe (
    stock_code VARCHAR(12) PRIMARY KEY,
    stock_name VARCHAR(200),
    hbm_flag BOOLEAN DEFAULT FALSE, hbf_flag BOOLEAN DEFAULT FALSE,
    cxl_flag BOOLEAN DEFAULT FALSE, pim_flag BOOLEAN DEFAULT FALSE,
    ai_server_flag BOOLEAN DEFAULT FALSE, packaging_flag BOOLEAN DEFAULT FALSE,
    osat_flag BOOLEAN DEFAULT FALSE, foundry_flag BOOLEAN DEFAULT FALSE,
    weight_score NUMERIC(8,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mcp4.semiconductor_score_daily (
    trade_date DATE, stock_code VARCHAR(12), stock_name VARCHAR(200),
    sox_score NUMERIC(8,2), nvda_score NUMERIC(8,2), hbm_score NUMERIC(8,2),
    flow_score NUMERIC(8,2), earnings_score NUMERIC(8,2),
    total_score NUMERIC(8,2), grade VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (trade_date, stock_code)
);

CREATE TABLE IF NOT EXISTS mcp4.institutional_score_daily (
    trade_date DATE, stock_code VARCHAR(12), stock_name VARCHAR(200),
    market_score NUMERIC(8,2), semiconductor_score NUMERIC(8,2),
    flow_score NUMERIC(8,2), earnings_score NUMERIC(8,2),
    valuation_score NUMERIC(8,2), risk_score NUMERIC(8,2),
    total_score NUMERIC(8,2), grade VARCHAR(10), signal VARCHAR(30),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (trade_date, stock_code)
);

CREATE INDEX IF NOT EXISTS idx_semiconductor_score_rank ON mcp4.semiconductor_score_daily(trade_date, total_score DESC);
CREATE INDEX IF NOT EXISTS idx_institutional_score_rank ON mcp4.institutional_score_daily(trade_date, total_score DESC);
