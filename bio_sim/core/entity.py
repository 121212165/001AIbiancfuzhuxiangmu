"""
生物实体基类
"""
import numpy as np
from typing import Tuple, List


class Entity:
    """生物实体基类"""

    def __init__(self, x: float, y: float, entity_id: int):
        self.id = entity_id
        self.position = np.array([x, y], dtype=float)
        self.velocity = np.array([0.0, 0.0], dtype=float)
        self.acceleration = np.array([0.0, 0.0], dtype=float)
        self.alive = True
        self.age = 0

    def update(self, dt: float = 1.0):
        """更新实体状态"""
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
        self.acceleration = np.array([0.0, 0.0])
        self.age += 1

    def apply_force(self, force: np.ndarray):
        """施加力"""
        self.acceleration += force

    def distance_to(self, other: 'Entity') -> float:
        """计算到另一个实体的距离"""
        return np.linalg.norm(self.position - other.position)

    def boundaries(self, width: int, height: int, margin: int = 10):
        """边界处理（弹跳）"""
        if self.position[0] < margin:
            self.position[0] = margin
            self.velocity[0] *= -1
        elif self.position[0] > width - margin:
            self.position[0] = width - margin
            self.velocity[0] *= -1

        if self.position[1] < margin:
            self.position[1] = margin
            self.velocity[1] *= -1
        elif self.position[1] > height - margin:
            self.position[1] = height - margin
            self.velocity[1] *= -1
