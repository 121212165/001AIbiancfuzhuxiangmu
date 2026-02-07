# 快速开始指南

> 5分钟上手生物模拟平台开发

---

## 🚀 快速安装

### 1. 克隆项目
```bash
git clone https://github.com/your-username/bio-sim.git
cd bio-sim
```

### 2. 创建虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行测试
```bash
python main.py
```

---

## 📖 核心概念

### 项目结构（5分钟理解）
```
bio_sim/
├── core/           # 📦 核心抽象层（不用动）
│   ├── SimulationBase    # 所有模拟的基类
│   └── Entity            # 生物实体的基类
│
├── simulations/    # 🔬 模拟实现（主要工作区）
│   ├── boids.py          # Boids算法
│   ├── ecosystem.py      # 生态系统
│   ├── game_of_life.py   # 生命游戏
│   └── genetic_algorithm.py # 遗传算法
│
├── visualizers/    # 🎨 可视化（渲染）
│   └── pygame_visualizer.py
│
└── utils/         # 🛠️ 工具（日志、配置）
```

### 创建新模拟（3步）

#### 步骤1: 创建模拟类
**文件**: `simulations/my_simulation.py`

```python
from core.simulation_base import SimulationBase
import numpy as np

class MySimulation(SimulationBase):
    """我的自定义模拟"""

    def __init__(self, width: int, height: int, config: dict = None):
        super().__init__(width, height, config)
        self.particles = []

    def initialize(self):
        """初始化 - 创建初始状态"""
        self.particles = [
            {'pos': np.random.rand(2) * [self.width, self.height]}
            for _ in range(100)
        ]

    def update(self):
        """更新 - 计算下一帧"""
        for p in self.particles:
            p['pos'] += np.random.randn(2)  # 随机移动
            # 边界处理
            p['pos'] = np.clip(p['pos'], [0, 0], [self.width, self.height])

    def get_state(self) -> dict:
        """返回状态给渲染器"""
        return {
            'positions': np.array([p['pos'] for p in self.particles])
        }
```

#### 步骤2: 添加渲染
**文件**: `visualizers/pygame_visualizer.py`

```python
def render_my_simulation(self, simulation):
    """渲染我的模拟"""
    self.screen.fill((20, 20, 30))

    state = simulation.get_state()
    for pos in state['positions']:
        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            (int(pos[0]), int(pos[1])),
            5
        )

    # 显示信息
    info = f"Particles: {len(state['positions'])} | Time: {simulation.time_step}"
    text = self.font.render(info, True, (255, 255, 255))
    self.screen.blit(text, (10, 10))
```

在 `render()` 方法中添加分支：
```python
def render(self, simulation):
    if simulation.__class__.__name__ == 'MySimulation':
        self.render_my_simulation(simulation)
    # ...
```

#### 步骤3: 运行
**文件**: `main.py`

```python
from simulations.my_simulation import MySimulation

def run_my_simulation():
    sim = MySimulation(800, 600, {'particle_count': 100})
    viz = PyGameVisualizer(800, 600)
    viz.run_simulation(sim)
```

或直接运行：
```bash
python -c "from visualizers.pygame_visualizer import PyGameVisualizer; \
from simulations.my_simulation import MySimulation; \
viz = PyGameVisualizer(800, 600); \
viz.run_simulation(MySimulation(800, 600))"
```

---

## 🧪 编写测试

**文件**: `tests/test_my_simulation.py`

```python
import pytest
import numpy as np
from simulations.my_simulation import MySimulation

def test_initialization():
    """测试初始化"""
    sim = MySimulation(100, 100)
    sim.initialize()
    assert len(sim.particles) > 0

def test_update():
    """测试更新"""
    sim = MySimulation(100, 100)
    sim.initialize()
    initial_positions = [p['pos'].copy() for p in sim.particles]
    sim.update()

    # 位置应该改变
    for i, p in enumerate(sim.particles):
        assert not np.array_equal(p['pos'], initial_positions[i])

def test_boundaries():
    """测试边界处理"""
    sim = MySimulation(100, 100)
    sim.initialize()

    for _ in range(100):
        sim.update()

    # 所有粒子应该在边界内
    for p in sim.particles:
        assert 0 <= p['pos'][0] <= 100
        assert 0 <= p['pos'][1] <= 100
```

运行测试：
```bash
pytest tests/test_my_simulation.py -v
```

---

## 🎨 常用模式

### 模式1: 使用配置
```python
# 使用配置字典
sim = MySimulation(800, 600, {
    'particle_count': 200,
    'speed': 2.0,
    'color': (255, 0, 0)
})

# 在代码中使用
def initialize(self):
    count = self.config.get('particle_count', 100)
    speed = self.config.get('speed', 1.0)
```

### 模式2: 添加实体
```python
from core.entity import Entity

class Particle(Entity):
    def __init__(self, x, y, id):
        super().__init__(x, y, id)
        self.color = (255, 255, 255)

    def update(self):
        # 自定义更新逻辑
        self.position += self.velocity
```

### 模式3: 统计数据
```python
def get_statistics(self) -> dict:
    """返回模拟统计"""
    return {
        'count': len(self.particles),
        'avg_speed': np.mean([p['speed'] for p in self.particles]),
        'time_step': self.time_step
    }
```

---

## 🔧 调试技巧

### 1. 使用日志
```python
from utils.logger import get_logger

class MySimulation(SimulationBase):
    def __init__(self, width, height, config=None):
        super().__init__(width, height, config)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("Simulation initialized")

    def update(self):
        self.logger.debug(f"Updating step {self.time_step}")
        # ...
```

### 2. 性能分析
```python
import time

def update(self):
    start = time.perf_counter()
    # 更新逻辑
    elapsed = time.perf_counter() - start
    if elapsed > 0.016:  # 超过16ms
        print(f"Warning: Update took {elapsed:.3f}s")
```

### 3. 可视化调试
```python
def render(self, simulation):
    # 正常渲染
    # ...

    # 调试信息
    debug_text = f"Debug: {simulation.get_statistics()}"
    text = self.font.render(debug_text, True, (255, 255, 0))
    self.screen.blit(text, (10, self.height - 30))
```

---

## 📚 推荐学习路径

### 初级（1-2天）
1. ✅ 运行现有模拟
2. ✅ 修改参数观察效果
3. ✅ 创建简单的粒子模拟

### 中级（1周）
1. ✅ 实现新的模拟类型
2. ✅ 添加交互功能
3. ✅ 编写完整测试

### 高级（2-4周）
1. ✅ 优化性能（向量化）
2. ✅ 实现复杂算法
3. ✅ 创建自定义可视化

---

## 🆘 常见问题

### Q: 如何调整模拟速度？
```python
# 在可视化器中
self.fps = 120  # 更高的FPS
```

### Q: 如何保存模拟状态？
```python
import json

state = {
    'time_step': sim.time_step,
    'particles': [p['pos'].tolist() for p in sim.particles]
}

with open('state.json', 'w') as f:
    json.dump(state, f)
```

### Q: 如何批量运行实验？
```python
for config in [
    {'particle_count': 50},
    {'particle_count': 100},
    {'particle_count': 200},
]:
    sim = MySimulation(800, 600, config)
    sim.initialize()
    for _ in range(1000):
        sim.step()
    # 记录结果...
```

---

## 🎯 下一步

- 📖 阅读 [完整文档](../README.md)
- 🗺️ 查看 [路线图](../ROADMAP.md)
- 🤝 参与 [贡献](../CONTRIBUTING.md)
- 💬 加入 [讨论](https://github.com/your-username/bio-sim/discussions)

---

## 💡 示例项目

### 示例1: 重力模拟
```python
class GravitySimulation(SimulationBase):
    def update(self):
        for p in self.particles:
            p['vel'][1] += 0.1  # 重力
            p['pos'] += p['vel']
```

### 示例2: 蚁群优化
```python
class AntColonySimulation(SimulationBase):
    def update(self):
        for ant in self.ants:
            # 信息素跟随
            if self.has_pheromone(ant.position):
                ant.follow_pheromone()
            # 随机探索
            else:
                ant.wander()
```

---

**开始探索生物模拟的世界吧！** 🌱

*有问题？查看 [FAQ](../FAQ.md) 或提 [Issue](https://github.com/your-username/bio-sim/issues)*
