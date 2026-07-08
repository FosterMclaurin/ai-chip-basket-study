-- Personal Portfolio EDA — DuckDB Schema
-- Run this first to initialize the database before any notebook work.
-- DuckDB is used over SQLite because it has CORR(), STDDEV(), ASOF JOIN,
-- and zero-copy handoff to pandas — all of which we need for stock analysis.

-- ─────────────────────────────────────────
-- TABLE 1: Daily stock prices (OHLCV)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS stock_prices (
    ticker      TEXT    NOT NULL,       -- e.g. 'NVDA', 'GOOGL', 'VTI'
    trade_date  DATE    NOT NULL,
    open_price  REAL,
    high_price  REAL,
    low_price   REAL,
    close_price REAL    NOT NULL,
    adj_close   REAL,                   -- dividend & split adjusted — use this for returns
    volume      BIGINT,
    PRIMARY KEY (ticker, trade_date)
);

CREATE INDEX IF NOT EXISTS idx_sp_ticker_date ON stock_prices (ticker, trade_date);

-- ─────────────────────────────────────────
-- TABLE 2: Portfolio holdings (the real stakes)
-- Snapshot of shares owned — joins against stock_prices
-- to compute position value, weights, and contribution to return.
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS holdings (
    ticker      TEXT    NOT NULL PRIMARY KEY,
    company     TEXT,
    sector      TEXT,                   -- 'Semiconductors', 'Big Tech', 'ETF — broad', ...
    is_etf      BOOLEAN DEFAULT FALSE,
    shares      REAL    NOT NULL,
    as_of_date  DATE    NOT NULL        -- when this snapshot was taken
);

-- This study uses an ILLUSTRATIVE EQUAL-WEIGHT allocation (1/15 per name),
-- not any real position sizes. If you want to populate holdings, insert your
-- own shares — e.g.:
--   INSERT INTO holdings VALUES ('NVDA','Nvidia','Semiconductors',FALSE,1.0,'2026-01-01');

-- ─────────────────────────────────────────
-- TABLE 3: Benchmark index
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS index_prices (
    trade_date  DATE NOT NULL PRIMARY KEY,
    spx_close   REAL NOT NULL,          -- ^GSPC — S&P 500
    ndx_close   REAL,                   -- ^NDX — Nasdaq 100 (tech-heavy comparison)
    sox_close   REAL                    -- ^SOX — Philly Semiconductor Index
);

-- ─────────────────────────────────────────
-- TABLE 4: Macro context
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS macro_data (
    trade_date   DATE NOT NULL PRIMARY KEY,
    us_10y_yield REAL,                  -- FRED DGS10 — rates drive tech valuations
    vix          REAL,                  -- ^VIX — market fear gauge
    dxy          REAL                   -- US Dollar Index
);

-- ─────────────────────────────────────────
-- USEFUL STARTER QUERIES (reference)
-- ─────────────────────────────────────────

-- Q1: Data inventory — what tickers do we have and how much data?
-- SELECT ticker, COUNT(*) AS rows, MIN(trade_date) AS first_date,
--        MAX(trade_date) AS last_date
-- FROM stock_prices GROUP BY ticker ORDER BY rows DESC;

-- Q2: Portfolio weights — what % of the portfolio is each position?
-- WITH latest AS (
--   SELECT ticker, adj_close,
--          ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY trade_date DESC) AS rn
--   FROM stock_prices
-- )
-- SELECT h.ticker, h.sector, h.shares * l.adj_close AS position_value,
--        ROUND(100.0 * h.shares * l.adj_close /
--          SUM(h.shares * l.adj_close) OVER (), 1) AS weight_pct
-- FROM holdings h JOIN latest l ON h.ticker = l.ticker AND l.rn = 1
-- ORDER BY position_value DESC;

-- Q3: Daily returns using LAG window function
-- WITH returns AS (
--   SELECT ticker, trade_date, adj_close,
--          (adj_close - LAG(adj_close) OVER (PARTITION BY ticker ORDER BY trade_date))
--            / LAG(adj_close) OVER (PARTITION BY ticker ORDER BY trade_date) AS daily_return
--   FROM stock_prices
-- )
-- SELECT * FROM returns WHERE daily_return IS NOT NULL;
