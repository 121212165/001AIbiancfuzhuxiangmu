"""
Boids群体行为模拟 - 实现鸟群/鱼群的群体行为
基于Craig Reynolds的Boids算法
"""
import numpy as np
from typing import List, Tuple
from core.entity import Entity
from core.simulation_base import SimulationBase


class Boid(Entity):
    """单个Boid实体"""

    def __init__(self, x: float, y: float, boid_id: int):
        super().__init__(x, y, boid_id)
        # 随机初始速度
        angle = np.random.uniform(0, 2 * np.pi)
        speed = np.random.uniform(2, 4)
        self.velocity = np.array([np.cos(angle) * speed, np.sin(angle) * speed])
        self.max_speed = 4.0
        self.max_force = 0.1
        self.perception_radius = 50

    def flock(self, boids: List['Boid'], params: dict) -> np.ndarray:
        """计算群体行为力"""
        alignment = self.align(boids)
        cohesion = self.cohere(boids)
        separation = self.separate(boids)

        # 应用权重
        alignment *= params.get('alignment_weight', 1.0)
        cohesion *= params.get('cohesion_weight', 1.0)
        separation *= params.get('separation_weight', 1.5)

        return alignment + cohesion + separation

    def align(self, boids: List['Boid']) -> np.ndarray:
        """对齐 - 向邻居的平均方向移动"""
        steering = np.array([0.0, 0.0])
        total = 0

        for other in boids:
            if other != self and self.distance_to(other) < self.perception_radius:
                steering += other.velocity
                total += 1

        if total > 0:
            steering /= total
            steering = (steering / np.linalg.norm(steering)) * self.max_speed
            steering -= self.velocity
            if np.linalg.norm(steering) > self.max_force:
                steering = (steering / np.linalg.norm(steering)) * self.max_force

        return steering

    def cohere(self, boids: List['Boid']) -> np.ndarray:
        """凝聚 - 向邻居的平均位置移动"""
        steering = np.array([0.0, 0.0])
        total = 0

        for other in boids:
            if other != self and self.distance_to(other) < self.perception_radius:
                steering += other.position
                total += 1

        if total > 0:
            steering /= total
            steering -= self.position
            if np.linalg.norm(steering) > 0:
                steering = (steering / np.linalg.norm(steering)) * self.max_speed
                steering -= self.velocity
                if np.linalg.norm(steering) > self.max_force:
                    steering = (steering / np.linalg.norm(steering)) * self.max_force

        return steering

    def separate(self, boids: List['Boid']) -> np.ndarray:
        """分离 - 避开太近的邻居"""
        steering = np.array([0.0, 0.0])
        total = 0
        desired_separation = 25

        for other in boids:
            d = self.distance_to(other)
            if other != self and d < desired_separation:
                diff = self.position - other.position
                if np.linalg.norm(diff) > 0:
                    diff /= np.linalg.norm(diff)
                steering += diff
                total += 1

        if total > 0:
            steering /= total
            if np.linalg.norm(steering) > 0:
                steering = (steering / np.linalg.norm(steering)) * self.max_speed
                steering -= self.velocity
                if np.linalg.norm(steering) > self.max_force:
                    steering = (steering / np.linalg.norm(steering)) * self.max_force

        return steering


class BoidsSimulation(SimulationBase):
    """Boids群体模拟"""

    def __init__(self, width: int, height: int, config: dict = None):
        default_config = {
            'num_boids': 100,
            'alignment_weight': 1.0,
            'cohesion_weight': 1.0,
            'separation_weight': 1.5
        }
        config = {**default_config, **(config or {})}

        super().__init__(width, height, config)
        self.boids: List[Boid] = []

    def initialize(self):
        """初始化boids"""
        self.boids = []
        for i in range(self.config['num_boids']):
            x = np.random.uniform(0, self.width)
            y = np.random.uniform(0, self.height)
            self.boids.append(Boid(x, y, i))

    def update(self):
        """更新所有boids"""
        for boid in self.boids:
            force = boid.flock(self.boids, self.config)
            boid.apply_force(force)
            boid.update()
            boid.boundaries(self.width, self.height)

    def get_state(self) -> np.ndarray:
        """获取用于渲染的状态"""
        positions = np.array([boid.position for boid in self.boids])
        velocities = np.array([boid.velocity for boid in self.boids])
        return {
            'positions': positions,
            'velocities': velocities
        }
