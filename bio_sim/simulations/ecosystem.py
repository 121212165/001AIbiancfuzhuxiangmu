"""
生态系统模拟 - 捕食者-猎物模型
基于Lotka-Volterra方程的个体基础模型
"""
import numpy as np
from typing import List
from core.entity import Entity
from core.simulation_base import SimulationBase


class Prey(Entity):
    """猎物（如兔子）"""

    def __init__(self, x: float, y: float, entity_id: int):
        super().__init__(x, y, entity_id)
        self.max_speed = 3.0
        self.energy = 100
        self.reproduction_rate = 0.005
        self.perception_radius = 80

    def update(self, dt: float = 1.0):
        super().update(dt)
        self.energy -= 0.1  # 基础代谢
        if self.energy <= 0:
            self.alive = False

    def eat(self, amount: float = 20):
        """进食增加能量"""
        self.energy += amount
        self.energy = min(self.energy, 150)

    def reproduce(self) -> bool:
        """繁殖"""
        if self.energy > 120 and np.random.random() < self.reproduction_rate:
            self.energy -= 60
            return True
        return False

    def flee(self, predators: List['Predator']) -> np.ndarray:
        """逃离捕食者"""
        steering = np.array([0.0, 0.0])

        closest_predator = None
        closest_dist = float('inf')

        for predator in predators:
            d = self.distance_to(predator)
            if d < self.perception_radius and d < closest_dist:
                closest_dist = d
                closest_predator = predator

        if closest_predator:
            diff = self.position - closest_predator.position
            if np.linalg.norm(diff) > 0:
                diff = (diff / np.linalg.norm(diff)) * self.max_speed
                steering = diff - self.velocity

        return steering


class Predator(Entity):
    """捕食者（如狼）"""

    def __init__(self, x: float, y: float, entity_id: int):
        super().__init__(x, y, entity_id)
        self.max_speed = 3.5
        self.energy = 150
        self.reproduction_rate = 0.002
        self.perception_radius = 120

    def update(self, dt: float = 1.0):
        super().update(dt)
        self.energy -= 0.15  # 捕食者代谢更快
        if self.energy <= 0:
            self.alive = False

    def eat(self, amount: float = 80):
        """捕食成功"""
        self.energy += amount
        self.energy = min(self.energy, 200)

    def reproduce(self) -> bool:
        """繁殖"""
        if self.energy > 180 and np.random.random() < self.reproduction_rate:
            self.energy -= 100
            return True
        return False

    def hunt(self, prey_list: List[Prey]) -> np.ndarray:
        """追踪猎物"""
        steering = np.array([0.0, 0.0])

        closest_prey = None
        closest_dist = float('inf')

        for prey in prey_list:
            if not prey.alive:
                continue
            d = self.distance_to(prey)
            if d < self.perception_radius and d < closest_dist:
                closest_dist = d
                closest_prey = prey

        if closest_prey:
            diff = closest_prey.position - self.position
            if np.linalg.norm(diff) > 0:
                diff = (diff / np.linalg.norm(diff)) * self.max_speed
                steering = diff - self.velocity

            # 捕获猎物
            if closest_dist < 5:
                closest_prey.alive = False
                self.eat(80)

        return steering


class EcosystemSimulation(SimulationBase):
    """生态系统模拟"""

    def __init__(self, width: int, height: int, config: dict = None):
        default_config = {
            'initial_prey': 50,
            'initial_predators': 10,
            'grass_growth_rate': 0.1
        }
        config = {**default_config, **(config or {})}

        super().__init__(width, height, config)
        self.prey: List[Prey] = []
        self.predators: List[Predator] = []
        self.grass = np.random.rand(height, width)  # 草的资源分布

    def initialize(self):
        """初始化生态系统"""
        self.prey = []
        self.predators = []
        self.grass = np.random.rand(self.height, self.width)

        # 创建初始猎物
        for i in range(self.config['initial_prey']):
            x = np.random.uniform(0, self.width)
            y = np.random.uniform(0, self.height)
            self.prey.append(Prey(x, y, i))

        # 创建初始捕食者
        for i in range(self.config['initial_predators']):
            x = np.random.uniform(0, self.width)
            y = np.random.uniform(0, self.height)
            self.predators.append(Predator(x, y, i))

    def update(self):
        """更新生态系统"""
        # 草生长
        self.grass = np.minimum(self.grass + self.config['grass_growth_rate'],
                                np.ones((self.height, self.width)))

        # 更新猎物
        new_prey = []
        for prey in self.prey:
            # 吃草
            grid_x, grid_y = int(prey.position[0]), int(prey.position[1])
            if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
                if self.grass[grid_y, grid_x] > 0.3:
                    prey.eat(10)
                    self.grass[grid_y, grid_x] = 0

            # 逃离捕食者
            flee_force = prey.flee(self.predators)
            prey.apply_force(flee_force)

            # 随机移动
            wander = np.random.uniform(-1, 1, 2)
            prey.apply_force(wander * 0.5)

            prey.update()
            prey.boundaries(self.width, self.height)

            # 繁殖
            if prey.reproduce():
                new_prey.append(Prey(prey.position[0], prey.position[1],
                                    len(self.prey) + len(new_prey)))

        self.prey.extend(new_prey)

        # 更新捕食者
        new_predators = []
        for predator in self.predators:
            # 追踪猎物
            hunt_force = predator.hunt(self.prey)
            predator.apply_force(hunt_force)

            # 随机移动
            wander = np.random.uniform(-1, 1, 2)
            predator.apply_force(wander * 0.3)

            predator.update()
            predator.boundaries(self.width, self.height)

            # 繁殖
            if predator.reproduce():
                new_predators.append(Predator(predator.position[0], predator.position[1],
                                             len(self.predators) + len(new_predators)))

        self.predators.extend(new_predators)

        # 移除死亡实体
        self.prey = [p for p in self.prey if p.alive]
        self.predators = [p for p in self.predators if p.alive]

    def get_state(self) -> dict:
        """获取用于渲染的状态"""
        prey_positions = np.array([p.position for p in self.prey]) if self.prey else np.empty((0, 2))
        predator_positions = np.array([p.position for p in self.predators]) if self.predators else np.empty((0, 2))

        return {
            'prey_positions': prey_positions,
            'predator_positions': predator_positions,
            'grass': self.grass
        }

    def get_statistics(self) -> dict:
        """获取统计数据"""
        return {
            'prey_count': len(self.prey),
            'predator_count': len(self.predators),
            'time_step': self.time_step
        }
