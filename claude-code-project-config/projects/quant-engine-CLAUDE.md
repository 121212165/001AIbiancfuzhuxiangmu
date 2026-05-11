# quant-engine

Python 量化交易引擎。

## Tech Stack

- **Language:** Python
- **Data:** pandas, akshare, yfinance, baostock
- **UI:** Streamlit
- **AI:** OpenAI API
- **Infra:** Redis
- **Testing:** pytest

## Architecture

```
core/           → Core trading engine
data/           → Data fetching & processing
strategy/       → Trading strategies
backtest/       → Backtesting engine
execution/      → Order execution
factors/        → Factor models
config/         → Configuration
runners/        → Runner scripts
ui/             → Streamlit UI
tests/          → Test suite
```

## Common Commands

```bash
pip install -r requirements.txt
pytest                     # Run tests
streamlit run demo_ui.py   # Launch UI
python test_demo.py        # Quick demo
```

## Code Conventions

- 配置在 `config/` 中用 YAML/Python
- 策略在 `strategy/` 中独立文件
- 回测在 `backtest/` 中，与策略分离
- Streamlit UI 在 `ui/` 中

> Detailed conventions: [quant-engine rules](../.claude/rules/projects/quant-engine.md)
