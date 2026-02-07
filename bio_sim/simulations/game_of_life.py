"""
康威生命游戏 - 细胞自动机
经典的零玩家游戏，展示复杂行为如何从简单规则中涌现
"""
import numpy as np
from core.simulation_base import SimulationBase


class GameOfLife(SimulationBase):
    """康威生命游戏模拟"""

    def __init__(self, width: int, height: int, config: dict = None):
        default_config = {
            'random_init': True,
            'density': 0.3,
            'wrap_around': True
        }
        config = {**default_config, **(config or {})}
        super().__init__(width, height, config)
        self.grid = np.zeros((height, width), dtype=int)

    def initialize(self):
        """初始化网格"""
        if self.config.get('random_init', True):
            self.grid = np.random.choice(
                [0, 1],
                size=(self.height, self.width),
                p=[1 - self.config['density'], self.config['density']]
            )
        else:
            # 可以加载预设模式
            self.grid = np.zeros((self.height, self.width), dtype=int)

    def count_neighbors(self, x: int, y: int) -> int:
        """计算邻居数量"""
        count = 0

        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                if self.config.get('wrap_around', True):
                    # 环绕边界
                    nx = (x + dx) % self.width
                    ny = (y + dy) % self.height
                else:
                    nx, ny = x + dx, y + dy
                    if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height:
                        continue

                count += self.grid[ny, nx]

        return count

    def update(self):
        """更新一代"""
        new_grid = self.grid.copy()

        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)

                # 生命游戏规则
                if self.grid[y, x] == 1:  # 存活
                    if neighbors < 2 or neighbors > 3:
                        new_grid[y, x] = 0  # 死亡
                else:  # 死亡
                    if neighbors == 3:
                        new_grid[y, x] = 1  # 复活

        self.grid = new_grid

    def get_state(self) -> np.ndarray:
        """获取用于渲染的状态"""
        return self.grid

    def set_pattern(self, pattern: np.ndarray, offset_x: int, offset_y: int):
        """在指定位置放置模式"""
        h, w = pattern.shape
        self.grid[offset_y:offset_y+h, offset_x:offset_x+w] = pattern

    def get_glider_pattern(self) -> np.ndarray:
        """获取滑翔机模式"""
        return np.array([
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ])

    def get_blinker_pattern(self) -> np.ndarray:
        """获取闪烁器模式"""
        return np.array([
            [1, 1, 1]
        ])

    def get_statistics(self) -> dict:
        """获取统计数据"""
        return {
            'live_cells': np.sum(self.grid),
            'time_step': self.time_step,
            'density': np.sum(self.grid) / (self.width * self.height)
        }
