# 贡献指南

感谢您对生物模拟平台的关注！我们欢迎各种形式的贡献。

## 开发环境设置

### 1. Fork 并克隆仓库

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

### 3. 安装开发依赖

```bash
make install-dev
# 或
pip install -e ".[dev]"
pre-commit install
```

## 代码规范

### Python 版本
- 支持 Python 3.8+
- 目标 Python 3.10

### 代码风格
- 使用 **Black** 进行代码格式化
- 使用 **isort** 进行导入排序
- 遵循 **PEP 8** 规范

```bash
make format  # 自动格式化
```

### 代码检查
- **flake8**: PEP 8 检查
- **pylint**: 代码质量检查
- **mypy**: 类型检查

```bash
make lint  # 运行所有检查
```

### 类型提示
所有函数应包含类型提示：

```python
def calculate_fitness(self, target: np.ndarray) -> float:
    """计算适应度。"""
    pass
```

### 文档字符串
使用 Google 风格的文档字符串：

```python
def simulate(self, steps: int) -> dict:
    """
    运行模拟指定步数。

    Args:
        steps: 要运行的步数

    Returns:
        包含模拟结果的字典

    Raises:
        ValueError: 如果 steps 为负数

    Example:
        >>> sim.simulate(100)
        {'time_step': 100, 'data': ...}
    """
    pass
```

## 测试

### 编写测试
- 使用 **pytest** 框架
- 测试文件命名: `test_*.py`
- 测试函数命名: `test_*`

```python
class TestMySimulation:
    def test_initialization(self):
        """测试初始化。"""
        sim = MySimulation(100, 100)
        assert sim.width == 100

    def test_update(self):
        """测试更新。"""
        sim = MySimulation(100, 100)
        sim.initialize()
        sim.step()
        assert sim.time_step == 1
```

### 运行测试

```bash
make test      # 运行所有测试
make test-cov  # 运行测试并生成覆盖率报告
```

### 测试覆盖率目标
- 目标: >80%
- 关键模块: >90%

## 提交代码

### Commit 消息规范
使用清晰的 commit 消息：

```
类型(范围): 简短描述

详细描述（可选）

类型:
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式（不影响功能）
- refactor: 重构
- test: 添加测试
- chore: 构建/工具链更新

示例:
feat(boids): 添加回避障碍物行为
fix(ecosystem): 修复捕食者繁殖条件错误
docs(readme): 更新安装说明
```

### Pull Request 流程

1. 更新主分支
   ```bash
   git checkout main
   git pull upstream main
   ```

2. 创建特性分支
   ```bash
   git checkout -b feature/my-feature
   ```

3. 编写代码和测试
   ```bash
   # 开发...
   make test  # 确保测试通过
   make lint  # 确保代码检查通过
   ```

4. 提交更改
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   ```

5. 推送到 GitHub
   ```bash
   git push origin feature/my-feature
   ```

6. 创建 Pull Request
   - 在 GitHub 上创建 PR
   - 填写 PR 模板
   - 等待代码审查

## 项目结构约定

### 添加新模拟

1. 在 `simulations/` 创建新文件
2. 继承 `SimulationBase` 类
3. 实现必需方法：`initialize()`, `update()`, `get_state()`
4. 在 `visualizers/pygame_visualizer.py` 添加渲染方法
5. 在 `main.py` 添加入口
6. 编写测试到 `tests/test_<simulation>.py`

### 代码组织

```
bio_sim/
├── core/           # 核心抽象类和接口
├── simulations/    # 具体模拟实现
├── visualizers/    # 渲染和可视化
├── utils/          # 工具函数
└── tests/          # 测试代码
```

## 问题反馈

### 报告 Bug
使用 GitHub Issues，包含：
- Python 版本
- 复现步骤
- 期望行为 vs 实际行为
- 错误日志（如果有）

### 功能请求
描述：
- 使用场景
- 期望的功能
- 可能的实现方案

## 代码审查

审查者会检查：
- 代码风格符合规范
- 测试覆盖充分
- 文档完整
- 没有引入新的警告
- 性能影响可接受

## 发布流程

1. 更新版本号
2. 更新 CHANGELOG
3. 创建 git tag
4. 构建并发布到 PyPI

## 许可证

贡献的代码将使用 MIT 许可证发布。

---

有任何问题？欢迎在 Issues 中讨论！
