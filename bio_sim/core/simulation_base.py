"""
生物模拟平台 - 核心模拟引擎基类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import numpy as np


class SimulationBase(ABC):
    """所有模拟类的基类"""

    def __init__(self, width: int, height: int, config: Dict[str, Any] = None):
        self.width = width
        self.height = height
        self.config = config or {}
        self.time_step = 0
        self.running = False

    @abstractmethod
    def initialize(self):
        """初始化模拟环境"""
        pass

    @abstractmethod
    def update(self):
        """更新一步模拟"""
        pass

    @abstractmethod
    def get_state(self) -> np.ndarray:
        """获取当前状态用于渲染"""
        pass

    def step(self):
        """执行一步模拟"""
        self.update()
        self.time_step += 1

    def reset(self):
        """重置模拟"""
        self.time_step = 0
        self.initialize()

    def get_info(self) -> Dict[str, Any]:
        """获取模拟信息"""
        return {
            'time_step': self.time_step,
            'width': self.width,
            'height': self.height,
            'config': self.config
        }
