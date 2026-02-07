"""
遗传算法进化模拟 - 模拟生物进化和自然选择
"""
import numpy as np
from typing import List, Tuple, Callable
from core.simulation_base import SimulationBase


class DNA:
    """DNA类 - 表示个体的基因"""

    def __init__(self, genes: np.ndarray = None, length: int = 50):
        if genes is not None:
            self.genes = genes
        else:
            self.genes = np.random.uniform(-1, 1, length)

    def crossover(self, partner: 'DNA') -> 'DNA':
        """交叉 - 与伴侣的基因混合"""
        midpoint = np.random.randint(0, len(self.genes))
        new_genes = np.concatenate([self.genes[:midpoint], partner.genes[midpoint:]])
        return DNA(new_genes)

    def mutate(self, rate: float = 0.01):
        """变异 - 随机改变基因"""
        for i in range(len(self.genes)):
            if np.random.random() < rate:
                self.genes[i] = np.random.uniform(-1, 1)


class Agent:
    """进化的代理（个体）"""

    def __init__(self, dna: DNA = None, dna_length: int = 50):
        self.dna = dna if dna else DNA(length=dna_length)
        self.fitness = 0.0
        self.age = 0

    def calculate_fitness(self, target: np.ndarray):
        """计算适应度 - 与目标的相似度"""
        diff = np.abs(self.dna.genes - target)
        self.fitness = 1.0 / (1.0 + np.sum(diff))

    def update(self):
        """更新个体状态"""
        self.age += 1


class Population:
    """种群"""

    def __init__(self, size: int, dna_length: int, mutation_rate: float = 0.01):
        self.size = size
        self.dna_length = dna_length
        self.mutation_rate = mutation_rate
        self.agents: List[Agent] = []
        self.generation = 0
        self.best_fitness = 0.0
        self.average_fitness = 0.0

        # 初始化种群
        for _ in range(size):
            self.agents.append(Agent(dna_length=dna_length))

    def evaluate(self, target: np.ndarray):
        """评估所有个体的适应度"""
        total_fitness = 0.0
        max_fitness = 0.0

        for agent in self.agents:
            agent.calculate_fitness(target)
            total_fitness += agent.fitness
            if agent.fitness > max_fitness:
                max_fitness = agent.fitness

        self.best_fitness = max_fitness
        self.average_fitness = total_fitness / len(self.agents)

    def selection(self) -> Agent:
        """选择 - 使用轮盘赌选择"""
        index = int(np.random.random() * len(self.agents))
        r = np.random.random()

        while r > 0:
            r -= self.agents[index].fitness / (self.average_fitness * len(self.agents))
            index = (index + 1) % len(self.agents)

        return self.agents[index]

    def reproduce(self) -> 'Population':
        """繁殖 - 创建新一代"""
        new_agents = []

        # 精英保留 - 保留最好的个体
        sorted_agents = sorted(self.agents, key=lambda a: a.fitness, reverse=True)
        elite_count = max(1, int(self.size * 0.1))
        for i in range(elite_count):
            elite = Agent(dna=sorted_agents[i].dna, dna_length=self.dna_length)
            elite.fitness = sorted_agents[i].fitness
            new_agents.append(elite)

        # 繁殖剩余个体
        while len(new_agents) < self.size:
            parent_a = self.selection()
            parent_b = self.selection()

            # 交叉
            child_dna = parent_a.dna.crossover(parent_b.dna)

            # 变异
            child_dna.mutate(self.mutation_rate)

            child = Agent(dna=child_dna, dna_length=self.dna_length)
            new_agents.append(child)

        # 创建新种群
        new_population = Population(self.size, self.dna_length, self.mutation_rate)
        new_population.agents = new_agents
        new_population.generation = self.generation + 1

        return new_population


class GeneticSimulation(SimulationBase):
    """遗传算法模拟 - 进化出目标基因"""

    def __init__(self, width: int, height: int, config: dict = None):
        default_config = {
            'population_size': 100,
            'dna_length': 100,
            'mutation_rate': 0.01,
            'target_type': 'random'  # 'random', 'pattern', 'zeros'
        }
        config = {**default_config, **(config or {})}
        super().__init__(width, height, config)
        self.population = None
        self.target = None
        self.best_genes_history = []

    def initialize(self):
        """初始化模拟"""
        # 生成目标基因
        dna_length = self.config['dna_length']

        if self.config['target_type'] == 'random':
            self.target = np.random.uniform(-1, 1, dna_length)
        elif self.config['target_type'] == 'pattern':
            # 创建一个模式
            self.target = np.sin(np.linspace(0, 4 * np.pi, dna_length))
        elif self.config['target_type'] == 'zeros':
            self.target = np.zeros(dna_length)

        # 创建初始种群
        self.population = Population(
            size=self.config['population_size'],
            dna_length=dna_length,
            mutation_rate=self.config['mutation_rate']
        )

        self.best_genes_history = []

    def update(self):
        """更新一代"""
        # 评估当前种群
        self.population.evaluate(self.target)

        # 记录最佳基因
        best_agent = max(self.population.agents, key=lambda a: a.fitness)
        self.best_genes_history.append(best_agent.dna.genes.copy())

        # 繁殖新一代
        self.population = self.population.reproduce()

    def get_state(self) -> dict:
        """获取用于渲染的状态"""
        if not self.population:
            return {}

        best_agent = max(self.population.agents, key=lambda a: a.fitness)

        return {
            'target': self.target,
            'best_genes': best_agent.dna.genes,
            'generation': self.population.generation,
            'best_fitness': self.population.best_fitness,
            'average_fitness': self.population.average_fitness,
            'history': self.best_genes_history[-100:] if self.best_genes_history else []
        }

    def get_statistics(self) -> dict:
        """获取统计数据"""
        if not self.population:
            return {}

        return {
            'generation': self.population.generation,
            'best_fitness': self.population.best_fitness,
            'average_fitness': self.population.average_fitness,
            'population_size': self.population.size
        }


class TargetSeekingSimulation(SimulationBase):
    """目标寻路模拟 - 代理进化学习找到目标"""

    def __init__(self, width: int, height: int, config: dict = None):
        default_config = {
            'population_size': 50,
            'lifespan': 200,
            'mutation_rate': 0.01,
            'max_force': 0.5,
            'max_speed': 4.0
        }
        config = {**default_config, **(config or {})}
        super().__init__(width, height, config)

        self.target = np.array([width * 0.8, height * 0.5])
        self.start = np.array([width * 0.2, height * 0.5])
        self.population = None
        self.obstacles = []

    def initialize(self):
        """初始化模拟"""
        from simulations.genetic_algorithm import RocketPopulation
        self.population = RocketPopulation(
            self.config['population_size'],
            self.start,
            self.config['lifespan'],
            self.config['max_force'],
            self.config['max_speed']
        )

    def update(self):
        """更新模拟"""
        if not self.population:
            return

        # 更新所有火箭
        self.population.update(self.target, self.obstacles)

        # 如果一代结束，进行自然选择
        if self.population.all_dead():
            self.population.evaluate(self.target)
            self.population = self.population.selection()

    def get_state(self) -> dict:
        """获取状态"""
        if not self.population:
            return {}

        return {
            'rockets': self.population.rockets,
            'target': self.target,
            'start': self.start,
            'generation': self.population.generation,
            'max_steps': self.population.lifespan,
            'current_step': self.population.current_step
        }


class Rocket:
    """火箭个体 - 用于目标寻路模拟"""

    def __init__(self, dna: DNA, start_pos: np.ndarray, max_force: float, max_speed: float):
        self.dna = dna
        self.pos = start_pos.copy()
        self.vel = np.array([0.0, 0.0])
        self.acc = np.array([0.0, 0.0])
        self.max_force = max_force
        self.max_speed = max_speed
        self.fitness = 0.0
        self.completed = False
        self.crashed = False
        self.gene_index = 0

    def apply_force(self, force: np.ndarray):
        """施加力"""
        self.acc += force

    def update(self, target: np.ndarray, obstacles: list, count: int):
        """更新火箭状态"""
        if not self.completed and not self.crashed:
            # 应用DNA中的力
            if count < len(self.dna.genes):
                angle = self.dna.genes[count] * np.pi * 2
                force = np.array([np.cos(angle), np.sin(angle)]) * self.max_force
                self.apply_force(force)

            # 更新物理
            self.vel += self.acc
            self.vel = np.clip(self.vel, -self.max_speed, self.max_speed)
            self.pos += self.vel
            self.acc *= 0

            # 检查是否到达目标
            d = np.linalg.norm(self.pos - target)
            if d < 10:
                self.completed = True
                self.pos = target.copy()

            # 检查边界碰撞
            if (self.pos[0] < 0 or self.pos[0] > 800 or
                self.pos[1] < 0 or self.pos[1] > 600):
                self.crashed = True

    def calc_fitness(self, target: np.ndarray):
        """计算适应度"""
        d = np.linalg.norm(self.pos - target)
        self.fitness = 1.0 / (d + 1.0)

        if self.completed:
            self.fitness *= 10.0

        if self.crashed:
            self.fitness /= 10.0


class RocketPopulation:
    """火箭种群"""

    def __init__(self, size: int, start_pos: np.ndarray,
                 lifespan: int, max_force: float, max_speed: float):
        self.size = size
        self.start_pos = start_pos
        self.lifespan = lifespan
        self.max_force = max_force
        self.max_speed = max_speed
        self.generation = 0
        self.current_step = 0

        self.rockets = []
        for i in range(size):
            genes = np.random.uniform(-1, 1, lifespan)
            dna = DNA(genes)
            self.rockets.append(Rocket(dna, start_pos, max_force, max_speed))

    def update(self, target: np.ndarray, obstacles: list):
        """更新所有火箭"""
        for rocket in self.rockets:
            rocket.update(target, obstacles, self.current_step)
        self.current_step += 1

    def all_dead(self) -> bool:
        """检查是否所有火箭都完成或坠毁"""
        return (self.current_step >= self.lifespan or
                all(r.completed or r.crashed for r in self.rockets))

    def evaluate(self, target: np.ndarray):
        """评估所有火箭"""
        for rocket in self.rockets:
            rocket.calc_fitness(target)

    def selection(self) -> 'RocketPopulation':
        """自然选择创建新一代"""
        # 计算最大适应度用于归一化
        max_fitness = max(r.fitness for r in self.rockets)

        new_rockets = []
        for i in range(self.size):
            # 选择父母
            parent_a = self.accept_reject(max_fitness)
            parent_b = self.accept_reject(max_fitness)

            # 交叉
            child_dna = parent_a.dna.crossover(parent_b.dna)

            # 变异
            child_dna.mutate(0.01)

            new_rockets.append(Rocket(child_dna, self.start_pos,
                                     self.max_force, self.max_speed))

        new_population = RocketPopulation(self.size, self.start_pos,
                                         self.lifespan, self.max_force, self.max_speed)
        new_population.rockets = new_rockets
        new_population.generation = self.generation + 1

        return new_population

    def accept_reject(self, max_fitness: float) -> Rocket:
        """接受-拒绝选择"""
        while True:
            index = np.random.randint(0, self.size)
            rocket = self.rockets[index]
            r = np.random.random() * max_fitness
            if r < rocket.fitness:
                return rocket
