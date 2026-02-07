"""Unit tests for simulation base classes."""
import pytest
import numpy as np
from core.simulation_base import SimulationBase
from core.entity import Entity


class DummySimulation(SimulationBase):
    """Dummy simulation for testing."""

    def __init__(self, width: int, height: int, config: dict = None):
        super().__init__(width, height, config)
        self.test_value = 0

    def initialize(self):
        """Initialize the simulation."""
        self.test_value = 42

    def update(self):
        """Update the simulation."""
        self.test_value += 1

    def get_state(self) -> np.ndarray:
        """Get the current state."""
        return np.array([self.test_value])


class TestSimulationBase:
    """Test cases for SimulationBase class."""

    def test_initialization(self):
        """Test simulation initialization."""
        sim = DummySimulation(100, 100)
        assert sim.width == 100
        assert sim.height == 100
        assert sim.time_step == 0
        assert sim.running is False

    def test_initialize_method(self):
        """Test initialize method."""
        sim = DummySimulation(100, 100)
        sim.initialize()
        assert sim.test_value == 42

    def test_step(self):
        """Test step method."""
        sim = DummySimulation(100, 100)
        sim.initialize()
        assert sim.time_step == 0
        sim.step()
        assert sim.time_step == 1
        assert sim.test_value == 43

    def test_reset(self):
        """Test reset method."""
        sim = DummySimulation(100, 100)
        sim.initialize()
        sim.step()
        sim.step()
        assert sim.time_step == 2
        sim.reset()
        assert sim.time_step == 0
        assert sim.test_value == 42

    def test_get_info(self):
        """Test get_info method."""
        sim = DummySimulation(100, 100, {"test_param": "value"})
        info = sim.get_info()
        assert info["width"] == 100
        assert info["height"] == 100
        assert info["time_step"] == 0
        assert info["config"]["test_param"] == "value"


class TestEntity:
    """Test cases for Entity class."""

    def test_entity_creation(self):
        """Test entity creation."""
        entity = Entity(50.0, 50.0, 1)
        assert entity.id == 1
        assert entity.position[0] == 50.0
        assert entity.position[1] == 50.0
        assert entity.alive is True
        assert entity.age == 0

    def test_apply_force(self):
        """Test apply_force method."""
        entity = Entity(50.0, 50.0, 1)
        force = np.array([1.0, 2.0])
        entity.apply_force(force)
        assert np.array_equal(entity.acceleration, force)

    def test_update(self):
        """Test update method."""
        entity = Entity(50.0, 50.0, 1)
        entity.velocity = np.array([1.0, 1.0])
        entity.update()
        assert entity.age == 1
        assert entity.position[0] == 51.0
        assert entity.position[1] == 51.0

    def test_distance_to(self):
        """Test distance_to method."""
        entity1 = Entity(0.0, 0.0, 1)
        entity2 = Entity(3.0, 4.0, 2)
        distance = entity1.distance_to(entity2)
        assert distance == 5.0

    def test_boundaries(self):
        """Test boundary handling."""
        entity = Entity(50.0, 50.0, 1)
        entity.velocity = np.array([-10.0, -10.0])
        entity.boundaries(100, 100, margin=10)
        assert entity.position[0] >= 10
        assert entity.position[1] >= 10
