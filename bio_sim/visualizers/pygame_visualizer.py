"""
PyGame可视化器 - 用于所有模拟的可视化
"""
import pygame
import numpy as np
from typing import Dict, Any
from core.simulation_base import SimulationBase


class PyGameVisualizer:
    """PyGame可视化器"""

    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.screen = None
        self.clock = None
        self.font = None
        self.running = False
        self.fps = 60

    def initialize(self):
        """初始化PyGame"""
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("生物模拟平台")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

    def render_boids(self, simulation):
        """渲染Boids模拟"""
        self.screen.fill((20, 20, 30))  # 深色背景

        state = simulation.get_state()
        positions = state['positions']
        velocities = state['velocities']

        # 绘制boids
        for i, pos in enumerate(positions):
            vel = velocities[i]
            # 计算方向角度
            angle = np.arctan2(vel[1], vel[0])

            # 绘制三角形
            triangle_length = 8
            p1 = pos + np.array([np.cos(angle), np.sin(angle)]) * triangle_length
            p2 = pos + np.array([np.cos(angle + 2.5), np.sin(angle + 2.5)]) * triangle_length * 0.6
            p3 = pos + np.array([np.cos(angle - 2.5), np.sin(angle - 2.5)]) * triangle_length * 0.6

            pygame.draw.polygon(self.screen, (100, 200, 255), [p1, p2, p3])

        # 显示信息
        info_text = f"Boids: {len(positions)} | Time: {simulation.time_step}"
        text_surface = self.font.render(info_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, 10))

    def render_ecosystem(self, simulation):
        """渲染生态系统模拟"""
        self.screen.fill((30, 40, 30))

        state = simulation.get_state()

        # 绘制草
        grass = state['grass']
        for y in range(0, self.height, 4):
            for x in range(0, self.width, 4):
                gy, gx = y * simulation.height // self.height, x * simulation.width // self.width
                if 0 <= gy < grass.shape[0] and 0 <= gx < grass.shape[1]:
                    intensity = int(grass[gy, gx] * 100)
                    pygame.draw.rect(self.screen, (30, 50 + intensity, 30), (x, y, 4, 4))

        # 绘制猎物（绿色圆圈）
        for pos in state['prey_positions']:
            pygame.draw.circle(self.screen, (100, 255, 100),
                             (int(pos[0] * self.width / simulation.width),
                              int(pos[1] * self.height / simulation.height)), 4)

        # 绘制捕食者（红色圆圈）
        for pos in state['predator_positions']:
            pygame.draw.circle(self.screen, (255, 100, 100),
                             (int(pos[0] * self.width / simulation.width),
                              int(pos[1] * self.height / simulation.height)), 6)

        # 显示统计信息
        stats = simulation.get_statistics()
        info_text = f"Prey: {stats['prey_count']} | Predators: {stats['predator_count']} | Time: {stats['time_step']}"
        text_surface = self.font.render(info_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, 10))

    def render_game_of_life(self, simulation):
        """渲染生命游戏"""
        self.screen.fill((0, 0, 0))

        grid = simulation.get_state()
        cell_size = max(1, min(self.width // simulation.width,
                               self.height // simulation.height))

        for y in range(simulation.height):
            for x in range(simulation.width):
                if grid[y, x] == 1:
                    screen_x = x * cell_size
                    screen_y = y * cell_size
                    pygame.draw.rect(self.screen, (0, 255, 100),
                                   (screen_x, screen_y, cell_size, cell_size))

        # 显示统计信息
        stats = simulation.get_statistics()
        info_text = f"Live Cells: {stats['live_cells']} | Generation: {stats['time_step']} | Density: {stats['density']:.3f}"
        text_surface = self.font.render(info_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, 10))

    def render_genetic_algorithm(self, simulation):
        """渲染遗传算法进化模拟"""
        self.screen.fill((30, 30, 40))

        state = simulation.get_state()

        # 绘制目标（红色）和最佳基因（绿色）
        target = state['target']
        best_genes = state['best_genes']

        if target is not None and best_genes is not None:
            # 绘制图表区域
            chart_x = 50
            chart_y = 100
            chart_width = self.width - 100
            chart_height = 200

            # 绘制目标线（红色）
            for i in range(len(target) - 1):
                x1 = chart_x + (i / len(target)) * chart_width
                y1 = chart_y + chart_height/2 - (target[i] * chart_height/2)
                x2 = chart_x + ((i + 1) / len(target)) * chart_width
                y2 = chart_y + chart_height/2 - (target[i + 1] * chart_height/2)
                pygame.draw.line(self.screen, (255, 100, 100), (x1, y1), (x2, y2), 2)

            # 绘制当前最佳基因（绿色）
            for i in range(len(best_genes) - 1):
                x1 = chart_x + (i / len(best_genes)) * chart_width
                y1 = chart_y + chart_height/2 - (best_genes[i] * chart_height/2)
                x2 = chart_x + ((i + 1) / len(best_genes)) * chart_width
                y2 = chart_y + chart_height/2 - (best_genes[i + 1] * chart_height/2)
                pygame.draw.line(self.screen, (100, 255, 100), (x1, y1), (x2, y2), 2)

            # 绘制图例
            pygame.draw.line(self.screen, (255, 100, 100), (50, 70), (100, 70), 2)
            target_text = self.font.render("目标基因", True, (255, 255, 255))
            self.screen.blit(target_text, (110, 60))

            pygame.draw.line(self.screen, (100, 255, 100), (250, 70), (300, 70), 2)
            current_text = self.font.render("当前最佳", True, (255, 255, 255))
            self.screen.blit(current_text, (310, 60))

            # 显示统计信息
            gen_text = f"Generation: {state['generation']}"
            fit_text = f"Best Fitness: {state['best_fitness']:.6f}"
            avg_text = f"Avg Fitness: {state['average_fitness']:.6f}"

            self.screen.blit(self.font.render(gen_text, True, (255, 255, 255)), (50, 350))
            self.screen.blit(self.font.render(fit_text, True, (100, 255, 100)), (50, 380))
            self.screen.blit(self.font.render(avg_text, True, (150, 200, 255)), (50, 410))

            # 绘制适应度历史曲线
            history_chart_y = 480
            history_chart_height = 100
            history = state.get('history', [])

            if len(history) > 1:
                for i in range(len(history) - 1):
                    x1 = chart_x + (i / len(history)) * chart_width
                    x2 = chart_x + ((i + 1) / len(history)) * chart_width
                    y1 = history_chart_y + history_chart_height - (history[i][0] if len(history[i]) > 0 else 0) * history_chart_height
                    y2 = history_chart_y + history_chart_height - (history[i+1][0] if len(history[i+1]) > 0 else 0) * history_chart_height
                    pygame.draw.line(self.screen, (255, 255, 100), (x1, y1), (x2, y2), 1)

    def render(self, simulation: SimulationBase):
        """根据模拟类型渲染"""
        if simulation.__class__.__name__ == 'BoidsSimulation':
            self.render_boids(simulation)
        elif simulation.__class__.__name__ == 'EcosystemSimulation':
            self.render_ecosystem(simulation)
        elif simulation.__class__.__name__ == 'GameOfLife':
            self.render_game_of_life(simulation)
        elif simulation.__class__.__name__ == 'GeneticSimulation':
            self.render_genetic_algorithm(simulation)
        else:
            self.screen.fill((50, 50, 50))
            text = self.font.render("Simulation not supported", True, (255, 255, 255))
            self.screen.blit(text, (self.width // 2 - 100, self.height // 2))

        pygame.display.flip()

    def handle_events(self, simulation):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    simulation.running = not simulation.running
                elif event.key == pygame.K_r:
                    simulation.reset()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def run_simulation(self, simulation: SimulationBase):
        """运行模拟循环"""
        self.initialize()
        simulation.initialize()
        simulation.running = True
        self.running = True

        while self.running:
            self.handle_events(simulation)

            if simulation.running:
                simulation.step()

            self.render(simulation)
            self.clock.tick(self.fps)

        pygame.quit()


def run_boids():
    """运行Boids模拟"""
    from simulations.boids import BoidsSimulation

    sim = BoidsSimulation(800, 600, {
        'num_boids': 150,
        'alignment_weight': 1.0,
        'cohesion_weight': 1.0,
        'separation_weight': 1.5
    })

    viz = PyGameVisualizer(800, 600)
    viz.run_simulation(sim)


def run_ecosystem():
    """运行生态系统模拟"""
    from simulations.ecosystem import EcosystemSimulation

    sim = EcosystemSimulation(800, 600, {
        'initial_prey': 80,
        'initial_predators': 15,
        'grass_growth_rate': 0.15
    })

    viz = PyGameVisualizer(800, 600)
    viz.run_simulation(sim)


def run_game_of_life():
    """运行生命游戏"""
    from simulations.game_of_life import GameOfLife

    sim = GameOfLife(100, 75, {
        'random_init': True,
        'density': 0.3
    })

    viz = PyGameVisualizer(800, 600)
    viz.run_simulation(sim)


def run_genetic_algorithm():
    """运行遗传算法模拟"""
    from simulations.genetic_algorithm import GeneticSimulation

    sim = GeneticSimulation(800, 600, {
        'population_size': 100,
        'dna_length': 100,
        'mutation_rate': 0.01,
        'target_type': 'pattern'
    })

    viz = PyGameVisualizer(800, 600)
    viz.run_simulation(sim)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        sim_type = sys.argv[1]
        if sim_type == 'boids':
            run_boids()
        elif sim_type == 'ecosystem':
            run_ecosystem()
        elif sim_type == 'life':
            run_game_of_life()
        elif sim_type == 'genetic':
            run_genetic_algorithm()
        else:
            print("Usage: python pygame_visualizer.py [boids|ecosystem|life|genetic]")
    else:
        print("Available simulations: boids, ecosystem, life, genetic")
        print("Usage: python pygame_visualizer.py [simulation_name]")
