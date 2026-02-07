# 生物模拟平台 (Bio-Simulation Platform)

<div align="center">

一个综合性的生物行为模拟平台，用于学习和研究复杂的生物系统行为。

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[代码规范](#规范化) • [测试](#测试) • [贡献](#贡献) • [规划](#项目规划)

</div>

## 特性

- **多种生物模拟**: Boids群体行为、生态系统、生命游戏、遗传算法
- **模块化设计**: 易于扩展新的模拟类型
- **可视化界面**: 基于PyGame的实时可视化
- **规范化开发**: 完整的测试、代码格式化和质量检查工具
- **配置管理**: 支持YAML配置文件和环境变量

## 项目结构

```
bio_sim/
├── core/                   # 核心模块
│   ├── simulation_base.py  # 模拟引擎基类
│   └── entity.py           # 生物实体基类
├── simulations/            # 模拟实现
│   ├── boids.py           # 群体行为模拟
│   ├── ecosystem.py       # 生态系统模拟
│   ├── game_of_life.py    # 细胞自动机
│   └── genetic_algorithm.py # 遗传算法
├── visualizers/           # 可视化工具
│   └── pygame_visualizer.py
├── utils/                 # 工具模块
│   ├── logger.py          # 日志系统
│   └── config.py          # 配置管理
├── tests/                 # 测试模块
├── config.yaml            # 配置文件
├── main.py                # 主入口
├── pyproject.toml         # 项目配置
└── requirements.txt       # 依赖列表
```

## 快速开始

### 安装

### 方式1: Docker（推荐）✨

```bash
# 克隆项目
git clone <repository-url>
cd bio_sim

# 构建镜像
make build

# 或使用 docker-compose
docker-compose build
```

### 方式2: 本地安装

```bash
# 克隆项目
git clone <repository-url>
cd bio_sim

# 安装依赖
pip install -r requirements.txt

# 或使用 Makefile
make install
```

### 运行

#### Docker方式（推荐）

```bash
# 查看所有命令
make help

# 运行交互式菜单
make run

# 或直接运行指定模拟
make boids       # 群体行为
make ecosystem   # 生态系统
make life        # 生命游戏
make genetic     # 遗传算法

# 开发模式
make up          # 启动开发容器
make shell       # 进入容器
make test        # 运行测试
```

#### 本地方式

```bash
# 使用交互式菜单
python main.py

# 或直接运行指定模拟
python -m visualizers.pygame_visualizer boids      # 群体行为
python -m visualizers.pygame_visualizer ecosystem  # 生态系统
python -m visualizers.pygame_visualizer life       # 生命游戏
python -m visualizers.pygame_visualizer genetic    # 遗传算法
```

## 模拟类型

### 1. Boids群体行为
模拟鸟群/鱼群的群体智能行为：
- 分离 (Separation)
- 对齐 (Alignment)
- 凝聚 (Cohesion)

### 2. 生态系统模拟
捕食者-猎物动态平衡模型：
- 猎物吃草、逃离捕食者、繁殖
- 捕食者追捕猎物、繁殖
- 草场自然生长

### 3. 康威生命游戏
经典细胞自动机：
- 活细胞周围有2-3个活邻居则存活
- 死细胞周围有3个活邻居则复活

### 4. 遗传算法
模拟生物进化过程：
- 选择 (Selection)
- 交叉 (Crossover)
- 变异 (Mutation)

## 操作说明

| 按键 | 功能 |
|------|------|
| 空格 | 暂停/继续 |
| R | 重置模拟 |
| ESC | 退出 |

## 规范化

本项目采用严格的开源项目规范：

### 代码格式化

```bash
# 自动格式化代码
make format

# 或手动执行
black .
isort .
```

### 代码检查

```bash
# 运行所有检查
make lint

# 或单独执行
flake8 .           # PEP 8 检查
pylint core/       # 代码质量检查
mypy core/         # 类型检查
```

### 测试

```bash
# 运行测试
make test

# 运行测试并生成覆盖率报告
make test-cov

# 或使用 pytest
pytest tests/ -v
pytest tests/ --cov=bio_sim --cov-report=html
```

### Pre-commit Hooks

```bash
# 安装 pre-commit hooks
make install-dev

# 或手动安装
pip install -e ".[dev]"
pre-commit install
```

### 配置文件

项目使用 `config.yaml` 进行配置管理：

```yaml
simulation:
  width: 800
  height: 600
  fps: 60

boids:
  num_boids: 150
  alignment_weight: 1.0
  # ... 更多配置
```

支持通过环境变量覆盖配置：

```bash
export BIO_SIM_WIDTH=1024
export BIO_SIM_HEIGHT=768
```

## 扩展开发

### 添加新模拟

1. 创建继承 `SimulationBase` 的类：

```python
from core.simulation_base import SimulationBase
import numpy as np

class MySimulation(SimulationBase):
    def __init__(self, width, height, config=None):
        super().__init__(width, height, config)

    def initialize(self):
        """初始化模拟"""
        pass

    def update(self):
        """更新一步"""
        pass

    def get_state(self):
        """返回渲染状态"""
        return np.array([])
```

2. 添加渲染方法到 `pygame_visualizer.py`：

```python
def render_my_simulation(self, simulation):
    """渲染新模拟"""
    state = simulation.get_state()
    # 渲染逻辑
```

3. 在 `render()` 方法中添加分支：

```python
elif simulation.__class__.__name__ == 'MySimulation':
    self.render_my_simulation(simulation)
```

## 开发工具

### Make 命令

```bash
make help       # 显示所有可用命令
make install    # 安装依赖
make format     # 格式化代码
make lint       # 运行检查
make test       # 运行测试
make clean      # 清理构建
make all        # 运行所有检查
```

## 代码质量标准

- **代码风格**: Black + isort
- **代码检查**: flake8 + pylint
- **类型检查**: mypy
- **测试框架**: pytest
- **测试覆盖率**: 目标 >80%

## 学习资源

- [Boids算法](http://www.red3d.com/cwr/boids/)
- [生命游戏](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)
- [Lotka-Volterra方程](https://en.wikipedia.org/wiki/Lotka%E2%80%93Volterra_equations)
- [遗传算法](https://en.wikipedia.org/wiki/Genetic_algorithm)

## 项目规划

查看详细的发展计划和路线图：

- 📋 [规划总览](docs/PLANNING_OVERVIEW.md) - 快速了解整体规划
- 🗺️ [完整路线图](ROADMAP.md) - 六个阶段的详细规划
- 📝 [第一阶段计划](docs/PHASE1_DETAILED_PLAN.md) - 当前阶段执行细节
- ✅ [任务追踪器](docs/TASK_TRACKER.md) - 每日任务和进度跟踪

### 开发路线

```
阶段1: 核心完善 (2周) → 阶段2: 功能扩展 (4周) → 阶段3: 可视化 (5周)
                                                                ↓
阶段6: 教育应用 ← 阶段5: 生态建设 (8周) ← 阶段4: 高级功能 (6周)
```

## 未来扩展

- [ ] 神经网络驱动的生物行为
- [ ] 更多细胞自动机规则
- [ ] 3D可视化支持
- [ ] 数据导出和分析工具
- [ ] GUI参数调节界面
- [ ] 分布式模拟支持

## 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

确保通过所有测试和代码检查：

```bash
make all  # 格式化、检查、测试
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
