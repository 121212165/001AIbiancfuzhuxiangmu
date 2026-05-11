# new-quant-strategy

Create a new trading strategy in quant-engine.

## Usage

Ask me to create a new strategy, specifying:
- Strategy name
- Data sources needed
- Entry/exit logic
- Risk parameters

## Generated Structure

```
strategy/<name>.py          → Strategy class
  - inherit from base strategy
  - implement generate_signals()
  - implement calculate_indicators()
backtest/<name>_backtest.py → Backtest script
  - load data
  - run strategy
  - output metrics
config/strategies/<name>.yaml → Strategy config
tests/test_<name>.py        → Tests
```

## Conventions

- One file per strategy in `strategy/`
- Parameters in config YAML, not hardcoded
- Data fetching separate from signal generation
- Backtest output includes: Sharpe, max drawdown, win rate, total return
