# 第一阶段详细执行计划

**时间规划**: 2周（14天）
**目标**: 将项目提升到生产就绪状态

---

## 第1周：代码质量与测试

### Day 1-2: 测试覆盖率提升

#### 任务1.1: 完善核心模块测试
**文件**: `tests/test_simulation_base.py`

- [ ] 添加 `SimulationBase` 边界测试
  - 测试负数宽高
  - 测试极大/极小值
  - 测试配置参数验证

- [ ] 添加 `Entity` 边界测试
  - 测试物理计算精度
  - 测试力累积
  - 测试位置更新边界情况

**验收标准**:
```bash
pytest tests/test_simulation_base.py --cov=core --cov-report=term-missing
# 目标: coverage > 90%
```

---

#### 任务1.2: 完善模拟测试
**文件**: `tests/test_ecosystem.py`, `tests/test_genetic.py`

**生态系统测试**:
```python
class TestEcosystemSimulation:
    def test_prey_reproduction(self):
        """测试猎物繁殖机制"""
        sim = EcosystemSimulation(200, 200)
        sim.initialize()
        initial_count = len(sim.prey)

        # 模拟足够长的时间让猎物繁殖
        for _ in range(1000):
            sim.update()

        assert len(sim.prey) > initial_count

    def test_predator_prey_balance(self):
        """测试捕食者-猎物动态平衡"""
        sim = EcosystemSimulation(200, 200)
        sim.initialize()

        # 记录种群动态
        prey_history = []
        predator_history = []

        for _ in range(2000):
            sim.update()
            prey_history.append(len(sim.prey))
            predator_history.append(len(sim.predators))

        # 检查是否有震荡模式
        assert len(sim.prey) > 0 or len(sim.predators) > 0
```

**遗传算法测试**:
```python
class TestGeneticAlgorithm:
    def test_convergence(self):
        """测试算法收敛性"""
        sim = GeneticSimulation(100, 100, {
            'population_size': 50,
            'dna_length': 20,
            'mutation_rate': 0.01
        })
        sim.initialize()

        best_fitness_history = []
        for _ in range(100):
            sim.step()
            best_fitness_history.append(sim.population.best_fitness)

        # 适应度应该随时间增加
        assert best_fitness_history[-1] > best_fitness_history[0]

    def test_diversity_maintenance(self):
        """测试种群多样性"""
        # 实现多样性测量
        pass
```

---

### Day 3-4: 性能分析与优化

#### 任务2.1: 性能分析

**工具**: Python cProfile, line_profiler

```bash
# 运行性能分析
python -m cProfile -o profile.stats main.py

# 可视化
pip install snakeviz
snakeviz profile.stats
```

**目标**: 识别每个模拟的性能瓶颈

**预期发现**:
- Boids: 距离计算（O(n²)）
- 生态系统: 空间查询
- 遗传算法: 适应度计算

---

#### 任务2.2: NumPy 向量化优化

**Boids 优化**:
```python
# 优化前（循环）
def align_slow(self, boids):
    steering = np.zeros(2)
    total = 0
    for other in boids:
        if self.distance_to(other) < self.perception_radius:
            steering += other.velocity
            total += 1
    return steering

# 优化后（向量化）
def align_fast(self, boids, positions, velocities):
    # 计算所有距离
    distances = np.linalg.norm(positions - self.position, axis=1)

    # 找到感知半径内的个体
    neighbors = distances < self.perception_radius

    # 计算平均速度
    avg_velocity = np.mean(velocities[neighbors], axis=0)

    return avg_velocity
```

**预期提升**: 3-5x 加速

---

#### 任务2.3: 空间分区优化

**实现网格空间索引**:

```python
# utils/spatial_hash.py
class SpatialHash:
    """空间哈希网格，用于快速邻近查询"""

    def __init__(self, cell_size: float, width: float, height: float):
        self.cell_size = cell_size
        self.grid = {}

    def insert(self, entity: Entity):
        """插入实体"""
        cell_x = int(entity.position[0] // self.cell_size)
        cell_y = int(entity.position[1] // self.cell_size)
        cell = (cell_x, cell_y)

        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(entity)

    def query(self, position: np.ndarray, radius: float) -> List[Entity]:
        """查询半径内的实体"""
        results = []
        cell_range = int(radius // self.cell_size) + 1
        center_x = int(position[0] // self.cell_size)
        center_y = int(position[1] // self.cell_size)

        for dx in range(-cell_range, cell_range + 1):
            for dy in range(-cell_range, cell_range + 1):
                cell = (center_x + dx, center_y + dy)
                if cell in self.grid:
                    results.extend(self.grid[cell])

        return results
```

**复杂度改进**: O(n²) → O(n)

---

### Day 5-7: 文档与类型提示

#### 任务3.1: 添加完整的类型提示

**改进前**:
```python
def update(self, config):
    if config.get('enabled'):
        return True
```

**改进后**:
```python
from typing import Dict, Any, Optional

def update(self, config: Dict[str, Any]) -> Optional[bool]:
    """
    Update simulation based on configuration.

    Args:
        config: Configuration dictionary with update parameters

    Returns:
        True if update was successful, None if disabled

    Raises:
        ValueError: If config is invalid
    """
    if config.get('enabled'):
        return True
    return None
```

**自动化检查**:
```bash
mypy core/ simulations/ visualizers/ --strict
```

---

#### 任务3.2: 生成 API 文档

**工具**: Sphinx + autodoc

**安装**:
```bash
pip install sphinx sphinx-rtd-theme
```

**配置**: `docs/source/conf.py`
```python
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

napoleon_google_docstring = True
napoleon_numpy_docstring = True
```

**生成文档**:
```bash
cd docs
sphinx-apidoc -o source ../bio_sim
make html
```

---

#### 任务3.3: 编写教程文档

**文档结构**:
```
docs/
├── tutorials/
│   ├── 01-getting-started.md
│   ├── 02-creating-simulation.md
│   ├── 03-visualization.md
│   ├── 04-advanced-features.md
│   └── 05-performance-tuning.md
└── examples/
    ├── simple_boids.py
    ├── custom_ecosystem.py
    └── data_analysis.py
```

---

## 第2周：功能增强与集成

### Day 8-9: 配置系统增强

#### 任务4.1: 实现配置验证

**文件**: `utils/config.py`

```python
from typing import Dict, Any, Type
import jsonschema

class Config:
    SCHEMA = {
        "type": "object",
        "properties": {
            "simulation": {
                "type": "object",
                "properties": {
                    "width": {"type": "integer", "minimum": 100, "maximum": 4096},
                    "height": {"type": "integer", "minimum": 100, "maximum": 4096},
                    "fps": {"type": "integer", "minimum": 1, "maximum": 240},
                },
                "required": ["width", "height"],
            },
            "boids": {
                "type": "object",
                "properties": {
                    "num_boids": {"type": "integer", "minimum": 1, "maximum": 10000},
                    "alignment_weight": {"type": "number", "minimum": 0, "maximum": 10},
                },
            },
        },
    }

    def validate(self) -> bool:
        """验证配置"""
        try:
            jsonschema.validate(self._config, self.SCHEMA)
            return True
        except jsonschema.ValidationError as e:
            raise ConfigError(f"Invalid configuration: {e.message}")
```

---

#### 任务4.2: 配置预设系统

```python
# utils/presets.py
PRESETS = {
    "fast_simulation": {
        "simulation": {"fps": 120, "width": 640, "height": 480},
        "boids": {"num_boids": 50},
    },
    "high_quality": {
        "simulation": {"fps": 60, "width": 1920, "height": 1080},
        "boids": {"num_boids": 500},
    },
    "benchmark": {
        "simulation": {"fps": 60, "width": 1280, "height": 720},
        "boids": {"num_boids": 2000},
    },
}

def load_preset(name: str) -> Dict[str, Any]:
    """加载预设配置"""
    if name not in PRESETS:
        raise ValueError(f"Unknown preset: {name}")
    return PRESETS[name].copy()
```

---

### Day 10-11: 日志系统增强

#### 任务5.1: 集成日志到模拟

```python
# core/simulation_base.py
from utils.logger import get_logger

class SimulationBase(ABC):
    def __init__(self, width, height, config=None):
        self.logger = get_logger(self.__class__.__name__)
        # ...

    def step(self):
        self.logger.debug(f"Step {self.time_step}")
        self.update()
        self.time_step += 1
```

---

#### 任务5.2: 性能日志

```python
import time
from contextlib import contextmanager

@contextmanager
def performance_logger(logger: logging.Logger, operation: str):
    """性能测量上下文管理器"""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info(f"{operation} took {elapsed:.4f}s")

# 使用
with performance_logger(self.logger, "Update"):
    self.update()
```

---

### Day 12-13: 交互功能

#### 任务6.1: 鼠标交互

```python
# visualizers/pygame_visualizer.py
class PyGameVisualizer:
    def __init__(self, width, height):
        # ...
        self.mouse_pos = None
        self.mouse_pressed = False

    def handle_events(self, simulation):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键添加实体
                    self.add_entity_at_mouse(simulation)
                elif event.button == 3:  # 右键移除
                    self.remove_entity_at_mouse(simulation)

    def add_entity_at_mouse(self, simulation):
        """在鼠标位置添加实体"""
        if simulation.__class__.__name__ == 'BoidsSimulation':
            boid = Boid(self.mouse_pos[0], self.mouse_pos[1],
                       len(simulation.boids))
            simulation.boids.append(boid)
```

---

#### 任务6.2: 参数调节界面

```python
# visualizers/ui.py
import imgui
import imgui.integrations.pygame as imgui_pygame

class ParameterPanel:
    """参数调节面板"""

    def __init__(self, simulation):
        self.simulation = simulation
        self.show = True

    def render(self):
        if not self.show:
            return

        imgui.begin("Parameters", True)

        if isinstance(self.simulation, BoidsSimulation):
            _, self.simulation.config['alignment_weight'] = imgui.slider_float(
                "Alignment", self.simulation.config['alignment_weight'], 0.0, 5.0
            )
            _, self.simulation.config['cohesion_weight'] = imgui.slider_float(
                "Cohesion", self.simulation.config['cohesion_weight'], 0.0, 5.0
            )

        imgui.end()
```

---

### Day 14: 测试与发布准备

#### 任务7.1: 集成测试

```python
# tests/integration/test_full_simulation.py
def test_full_simulation_workflow():
    """测试完整的模拟工作流"""
    # 1. 创建模拟
    sim = BoidsSimulation(800, 600)
    sim.initialize()

    # 2. 运行一段时间
    for _ in range(100):
        sim.step()

    # 3. 检查状态
    state = sim.get_state()
    assert len(state['positions']) == sim.config['num_boids']

    # 4. 重置
    sim.reset()
    assert sim.time_step == 0
```

---

#### 任务7.2: CI/CD 配置

**文件**: `.github/workflows/test.yml`
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        pip install -e ".[dev]"

    - name: Format check
      run: |
        black --check .
        isort --check-only .

    - name: Lint
      run: |
        flake8 .
        pylint core/ simulations/

    - name: Type check
      run: mypy core/ simulations/

    - name: Test
      run: pytest tests/ --cov=bio_sim --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

#### 任务7.3: 发布清单

- [ ] 更新版本号（`pyproject.toml`）
- [ ] 更新 CHANGELOG.md
- [ ] 运行完整测试套件
- [ ] 生成文档
- [ ] 创建 Git tag
- [ ] 构建 PyPI 包
- [ ] 测试 PyPI 安装

```bash
# 发布流程
bump2version patch  # 或 minor/major
git push origin main --tags
python -m build
twine upload dist/*
```

---

## 验收标准

### 代码质量
- [ ] 测试覆盖率 ≥ 80%
- [ ] 所有 mypy 检查通过
- [ ] 所有 pylint 检查通过（score ≥ 8.0）
- [ ] CI/CD 全部通过

### 性能
- [ ] Boids 模拟（1000个个体） ≥ 60 FPS
- [ ] 生态模拟（500实体） ≥ 30 FPS
- [ ] 内存使用 ≤ 500MB（标准配置）

### 文档
- [ ] API 文档完整
- [ ] 至少 3 个教程
- [ ] 5+ 个代码示例

### 用户体验
- [ ] 鼠标交互功能
- [ ] 参数调节面板
- [ ] 配置预设
- [ ] 清晰的错误信息

---

## 时间分配

| 任务 | 预计时间 | 缓冲时间 | 总计 |
|------|---------|---------|------|
| 测试完善 | 2天 | 0.5天 | 2.5天 |
| 性能优化 | 2天 | 1天 | 3天 |
| 文档编写 | 2天 | 0.5天 | 2.5天 |
| 功能增强 | 3天 | 1天 | 4天 |
| 发布准备 | 1天 | 0.5天 | 1.5天 |
| **总计** | **10天** | **3.5天** | **14天** |

---

## 风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 性能优化效果不明显 | 中 | 中 | 先分析后优化，准备备选方案 |
| 测试覆盖率提升困难 | 低 | 低 | 先关注核心模块，接受边缘代码低覆盖 |
| 文档编写耗时 | 高 | 低 | 使用自动化工具，逐步完善 |
| 依赖兼容性问题 | 低 | 高 | 使用虚拟环境，锁定版本 |

---

*本计划完成后，项目将达到生产就绪状态，为后续功能扩展奠定坚实基础。*
