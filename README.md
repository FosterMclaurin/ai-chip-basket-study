# Semiconductor-Tilted Portfolio: A Risk & Concentration Study

**What does it actually mean to hold a basket of 15 popular AI / semiconductor names?**
This is a reproducible exploratory data analysis (EDA) of a real-world-style tech-tilted equity
basket — the kind an enthusiastic 2024–2026 retail investor might have assembled. The goal isn't
stock tips; it's to show, with data, the **trade-off you take on when a portfolio leans hard into
one hot sector**: enormous upside, paired with concentrated, correlated, deep-drawdown risk.

> ⚠️ **Not investment advice.** Educational data analysis only. Weights are illustrative
> (equal-weight), not a recommendation. Past performance says nothing about the future.

## The basket (15 names)

| Ticker | Company | Bucket |
|--------|---------|--------|
| NVDA | Nvidia | Semiconductors |
| MU | Micron | Semiconductors |
| MRVL | Marvell | Semiconductors |
| AVGO | Broadcom | Semiconductors |
| SMH | VanEck Semiconductor ETF | Semi ETF |
| GOOGL | Alphabet | Big Tech |
| MSFT | Microsoft | Big Tech |
| CRWD | CrowdStrike | Cybersecurity |
| ANET | Arista Networks | Networking |
| APLD | Applied Digital | Data centers |
| PLTR | Palantir | Software / Defense |
| PL | Planet Labs | Space / Imaging |
| NASA | Tema Space Innovators ETF | Space ETF (launched ~Mar 2026) |
| VTI | Vanguard Total Market ETF | Broad-market benchmark |
| VOO | Vanguard S&P 500 ETF | Broad-market benchmark |

**Weighting:** equal-weight (1/15 each) for all portfolio-level figures. VOO/VTI double as the
built-in "boring benchmark" to compare against.
**Window:** 2024-01-01 → 2026-07-01 (~625 trading days). Data via `yfinance`, stored in DuckDB.

## Headline findings

### 1. The concentration bet paid off — and it was a real bet
| | Equal-weight basket* | VOO (S&P 500) |
|---|---|---|
| Total return | **+410%** | +63% |
| Annualized volatility | 35.0% | 15.5% |
| Max drawdown | −33.8% | −18.7% |

\*14 full-history names; NASA excluded from portfolio-level stats (only ~63 days of history).

**6.5× the S&P's return — but 2.3× the volatility and nearly 2× the worst drawdown.** The excess
return was not free; it was paid for in stomach.

### 2. A third of the basket is *directly* semiconductors
Equal-weight, **33.3%** sits in semis (NVDA, MU, MRVL, AVGO + the SMH ETF) before even looking
*through* the broad ETFs (VTI/VOO also hold NVDA/AVGO internally — true exposure is higher still).

### 3. The semis move as one — diversification is partly an illusion
Average pairwise **return** correlation among the semis (NVDA, MU, MRVL, AVGO, SMH) is **0.64**.
Holding five semiconductor tickers is closer to holding one big leveraged bet than to being
diversified. Across all 14 names the average correlation is 0.45.

### 4. Per-stock scorecard (2024-01 → 2026-07)
| Ticker | Total return | Ann. vol | Max drawdown |
|--------|-------------:|---------:|-------------:|
| MU | +1313% | 65% | −58% |
| PL | +1292% | 94% | −54% |
| PLTR | +604% | 64% | −48% |
| APLD | +436% | 127% | −72% |
| MRVL | +416% | 69% | −61% |
| NVDA | +316% | 49% | −37% |
| SMH | +291% | 38% | −36% |
| AVGO | +257% | 52% | −41% |
| CRWD | +209% | 48% | −44% |
| ANET | +194% | 52% | −50% |
| GOOGL | +161% | 31% | −30% |
| VOO | +63% | 16% | −19% |
| VTI | +62% | 16% | −19% |
| MSFT | +3% | 25% | −35% |
| NASA† | +21% | 69% | −37% |

†NASA has only ~63 trading days (recent launch) — figures shown for completeness but not
statistically comparable to the full-history names.

## Data-quality note
`NASA` (Tema Space Innovators ETF) returned only ~63 rows vs ~625 for every other name — consistent
with a ~March 2026 launch. It's real and tradeable but too young for long-window statistics
(moving averages, stable correlations), so it's flagged and excluded from portfolio aggregates.

## Reproduce it
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python analyze.py        # downloads data, loads DuckDB, prints every figure above
```

## Method notes
- Returns use **dividend/split-adjusted** close prices (`adj_close`) — the only correct series for
  return math.
- Correlations are computed on **daily returns, never on price levels** (price-level correlation is
  spuriously ~0.95 for almost any two rising stocks — the classic retail mistake).
- Equal-weight portfolio return is daily-rebalanced (mean of daily returns).

## Stack
`yfinance` (ingest) → `pandas` (reshape) → `DuckDB` (store + SQL) → `numpy` (stats).
