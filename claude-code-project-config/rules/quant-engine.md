# quant-engine Coding Conventions

## Strategy (`strategy/`)

- One class per file, standalone with `generate_signals(ticker, df, indicators) -> list[Signal]`
- Return `Signal` dataclass: `ticker`, `source`, `decision`, `confidence`, `metadata`
- Deploy via `PortfolioManager` (central arbitration layer)
- Strategy is environment-specific: trend vs. range vs. etc.

## Config (`config/`)

- YAML format with `default:` top-level key
- Per-market profiles: `cn:`, `us:`
- Per-mode profiles: `backtest:`, `live:`
- Parameters grouped by category with comment headers (`# -- RSI thresholds --`)

## Data Fetching (`data/`)

- Unified entry: `fetch_ohlcv(ticker, days, use_cache)`
- Returns normalized DataFrame: `[date, open, high, low, close, volume]`
- Market detection: 6-digit = China (akshare), else US (yfinance)
- 3-level cache: memory → file → Redis
- Publish events on completion

## Backtest (`backtest/`)

- `BacktestEngine` daily loop: mark-to-market → stop checks → analyze → execute → record
- Results as `BacktestResult` dataclass with `summary()`, `performance()`, `plot()`
- Key dataclasses: `BacktestConfig`, `TradeRecord`, `PerformanceMetrics`

## Python Style

- Dataclasses (`@dataclass`) for all data objects: `OHLCV`, `Position`, `Order`, `Signal`
- Enums for all fixed values: `Decision`, `MarketRegime`, `OrderStatus`
- Event bus: global singleton `events` with string-constant topics (`EVENT_*`)
- Private methods: `_` prefix
- Functions/files: `lowercase_with_underscores`
- Classes: `CamelCase`
- Constants: `SCREAMING_CASE`
