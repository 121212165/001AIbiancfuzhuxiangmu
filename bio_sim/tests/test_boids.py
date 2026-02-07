"""Unit tests for Boids simulation."""
import pytest
import numpy as np
from simulations.boids import Boid, BoidsSimulation


class TestBoid:
    """Test cases for Boid class."""

    def test_boid_creation(self):
        """Test boid creation."""
        boid = Boid(50.0, 50.0, 1)
        assert boid.id == 1
        assert boid.position[0] == 50.0
        assert boid.max_speed == 4.0
        assert boid.max_force == 0.1

    def test_align(self):
        """Test alignment behavior."""
        boid1 = Boid(50.0, 50.0, 1)
        boid1.velocity = np.array([1.0, 0.0])
        boid2 = Boid(55.0, 50.0, 2)
        boid2.velocity = np.array([1.0, 0.0])

        steering = boid1.align([boid1, boid2])
        assert isinstance(steering, np.ndarray)
        assert len(steering) == 2

    def test_cohere(self):
        """Test cohesion behavior."""
        boid1 = Boid(50.0, 50.0, 1)
        boid2 = Boid(55.0, 50.0, 2)

        steering = boid1.cohere([boid1, boid2])
        assert isinstance(steering, np.ndarray)
        assert len(steering) == 2

    def test_separate(self):
        """Test separation behavior."""
        boid1 = Boid(50.0, 50.0, 1)
        boid2 = Boid(52.0, 50.0, 2)  # Very close

        steering = boid1.separate([boid1, boid2])
        assert isinstance(steering, np.ndarray)
        assert len(steering) == 2


class TestBoidsSimulation:
    """Test cases for BoidsSimulation class."""

    def test_initialization(self):
        """Test simulation initialization."""
        sim = BoidsSimulation(800, 600, {"num_boids": 50})
        sim.initialize()
        assert len(sim.boids) == 50
        assert sim.time_step == 0

    def test_update(self):
        """Test update method."""
        sim = BoidsSimulation(800, 600, {"num_boids": 10})
        sim.initialize()
        initial_positions = [boid.position.copy() for boid in sim.boids]
        sim.update()
        assert sim.time_step == 1
        # Positions should have changed
        for i, boid in enumerate(sim.boids):
            assert not np.array_equal(boid.position, initial_positions[i])

    def test_get_state(self):
        """Test get_state method."""
        sim = BoidsSimulation(800, 600, {"num_boids": 10})
        sim.initialize()
        state = sim.get_state()
        assert "positions" in state
        assert "velocities" in state
        assert len(state["positions"]) == 10
        assert len(state["velocities"]) == 10

    def test_reset(self):
        """Test reset method."""
        sim = BoidsSimulation(800, 600, {"num_boids": 10})
        sim.initialize()
        sim.step()
        sim.step()
        assert sim.time_step == 2
        sim.reset()
        assert sim.time_step == 0
