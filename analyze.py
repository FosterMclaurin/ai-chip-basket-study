"""
Semiconductor-Tilted Portfolio — Risk & Concentration Study
Reproducible analysis: downloads prices, loads DuckDB, prints every figure in the README.

Educational only. Weights are illustrative (equal-weight), not investment advice.
"""
import duckdb
import pandas as pd
import numpy as np
import yfinance as yf

START, END = "2024-01-01", "2026-07-01"
DB = "portfolio.duckdb"

BASKET = {
    "NVDA": "Semis", "MU": "Semis", "MRVL": "Semis", "AVGO": "Semis", "SMH": "ETF-semis",
    "GOOGL": "Big Tech", "MSFT": "Big Tech", "CRWD": "Cybersecurity", "ANET": "Networking",
    "APLD": "Data centers", "PLTR": "Software/Defense", "PL": "Space/Imaging",
    "NASA": "ETF-space", "VTI": "ETF-broad", "VOO": "ETF-broad",
}


def ingest():
    """Download each ticker, reshape to tidy OHLCV, load into DuckDB."""
    frames = []
    for t in BASKET:
        df = yf.download(t, start=START, end=END, auto_adjust=False, progress=False)
        if df.empty:
            print(f"  {t}: NO DATA — skipping")
            continue
        df.columns = df.columns.droplevel(1)
        df = df.reset_index()
        df.insert(0, "ticker", t)
        df = df.rename(columns={
            "Date": "trade_date", "Open": "open_price", "High": "high_price",
            "Low": "low_price", "Close": "close_price", "Adj Close": "adj_close",
            "Volume": "volume"})
        frames.append(df)
        print(f"  {t}: {len(df)} rows")
    prices = pd.concat(frames, ignore_index=True)

    con = duckdb.connect(DB)
    con.execute(open("sql/schema.sql").read())
    con.execute("DELETE FROM stock_prices")
    con.execute("""INSERT INTO stock_prices
        SELECT ticker, trade_date, open_price, high_price, low_price,
               close_price, adj_close, volume FROM prices""")
    con.commit()
    con.close()
    print(f"Loaded {len(prices)} rows into {DB}\n")


def analyze():
    con = duckdb.connect(DB, read_only=True)
    df = con.execute(
        "SELECT ticker, trade_date, adj_close FROM stock_prices ORDER BY ticker, trade_date"
    ).df()
    con.close()

    piv = df.pivot(index="trade_date", columns="ticker", values="adj_close").sort_index()
    rets = piv.pct_change()

    # Per-stock scorecard
    print("=== Per-stock (2024-01 to 2026-07) ===")
    rows = []
    for t in piv.columns:
        s = piv[t].dropna()
        total = s.iloc[-1] / s.iloc[0] - 1
        vol = s.pct_change().std() * np.sqrt(252)
        dd = (s / s.cummax() - 1).min()
        rows.append((t, len(s), total, vol, dd))
    for t, n, total, vol, dd in sorted(rows, key=lambda r: -r[2]):
        print(f"{t:6} {n:4}d  ret {total:+7.1%}  vol {vol:6.1%}  maxDD {dd:7.1%}")

    # Equal-weight portfolio (exclude NASA: too little history)
    full = [c for c in piv.columns if c != "NASA"]
    ew = rets[full].mean(axis=1)
    curve = (1 + ew).cumprod()
    print("\n=== Equal-weight basket (NASA excluded) vs VOO ===")
    print(f"basket : ret {curve.iloc[-1]-1:+.1%}  vol {ew.std()*np.sqrt(252):.1%}  "
          f"maxDD {(curve/curve.cummax()-1).min():.1%}")
    vs = piv["VOO"]
    print(f"VOO    : ret {vs.iloc[-1]/vs.iloc[0]-1:+.1%}  vol {rets['VOO'].std()*np.sqrt(252):.1%}  "
          f"maxDD {(vs/vs.cummax()-1).min():.1%}")

    # Concentration
    counts = pd.Series(BASKET).value_counts()
    direct_semi = (counts.get("Semis", 0) + counts.get("ETF-semis", 0)) / len(BASKET)
    print(f"\nDirect semiconductor exposure (equal-weight) = {direct_semi:.1%}")

    # Correlation
    semis = ["NVDA", "MU", "MRVL", "AVGO", "SMH"]
    cm = rets[semis].corr().values[np.triu_indices(len(semis), 1)]
    all_c = rets[full].corr().values[np.triu_indices(len(full), 1)]
    print(f"Avg return-correlation among semis = {cm.mean():.2f}")
    print(f"Avg return-correlation across all 14 = {all_c.mean():.2f}")


if __name__ == "__main__":
    ingest()
    analyze()
