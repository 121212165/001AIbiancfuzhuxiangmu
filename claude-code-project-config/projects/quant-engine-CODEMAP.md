# CODEMAP

## Directory Responsibilities

| Path | Responsibility |
|------|---------------|
| `core/` | Trading engine, order management, portfolio tracking |
| `data/` | Market data fetching (akshare, yfinance, baostock), data cleaning |
| `strategy/` | Strategy definitions (one file per strategy) |
| `backtest/` | Backtesting framework, performance metrics |
| `execution/` | Order routing, broker integration |
| `factors/` | Alpha factor calculations |
| `config/` | Configuration files |
| `runners/` | Entry point scripts for different modes |
| `ui/` | Streamlit dashboard components |

## Data Flow

```
Data sources (akshare/yfinance)
  → data/ (fetch + clean)
  → factors/ (calculate factors)
  → strategy/ (generate signals)
  → core/ (execute trades)
  → backtest/ (validate) OR execution/ (live trade)
  → ui/ (display results)
```
