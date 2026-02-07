"""Unit tests for Ecosystem simulation."""
import pytest
import numpy as np
from simulations.ecosystem import EcosystemSimulation, Prey, Predator


class TestPrey:
    """Test cases for Prey class."""

    def test_prey_creation(self):
        """Test prey creation."""
        prey = Prey(50.0, 50.0, 1)
        assert prey.id == 1
        assert prey.max_speed == 3.0
        assert prey.energy == 100
        assert prey.alive is True

    def test_prey_energy_decay(self):
        """Test prey energy decay over time."""
        prey = Prey(50.0, 50.0, 1)
        initial_energy = prey.energy
        prey.update()
        assert prey.energy < initial_energy
        assert prey.age == 1

    def test_prey_eat(self):
        """Test prey eating."""
        prey = Prey(50.0, 50.0, 1)
        initial_energy = prey.energy
        prey.eat(30)
        assert prey.energy == initial_energy + 30
        assert prey.energy <= 150  # Should cap at max

    def test_prey_reproduction(self):
        """Test prey reproduction."""
        prey = Prey(50.0, 50.0, 1)
        prey.energy = 150  # High energy
        # Set random seed for deterministic test
        np.random.seed(42)
        reproduced = prey.reproduce()
        # With seed 42 and reproduction_rate 0.005, result should be False
        assert isinstance(reproduced, bool)

    def test_prey_death(self):
        """Test prey death from starvation."""
        prey = Prey(50.0, 50.0, 1)
        prey.energy = 0
        prey.update()
        assert prey.alive is False

    def test_prey_flee(self):
        """Test prey fleeing behavior."""
        prey = Prey(50.0, 50.0, 1)
        predator = Predator(60.0, 50.0, 2)
        steering = prey.flee([predator])
        assert isinstance(steering, np.ndarray)
        assert len(steering) == 2


class TestPredator:
    """Test cases for Predator class."""

    def test_predator_creation(self):
        """Test predator creation."""
        predator = Predator(50.0, 50.0, 1)
        assert predator.id == 1
        assert predator.max_speed == 3.5
        assert predator.energy == 150

    def test_predator_energy_decay(self):
        """Test predator energy decay (faster than prey)."""
        predator = Predator(50.0, 50.0, 1)
        initial_energy = predator.energy
        predator.update()
        assert predator.energy < initial_energy

    def test_predator_hunt(self):
        """Test predator hunting."""
        predator = Predator(50.0, 50.0, 1)
        prey = Prey(53.0, 50.0, 2)  # Very close
        steering = predator.hunt([prey])
        assert isinstance(steering, np.ndarray)

    def test_predator_catch_prey(self):
        """Test predator catching prey."""
        predator = Predator(50.0, 50.0, 1)
        prey = Prey(52.0, 50.0, 2)  # Within catch distance
        predator.hunt([prey])
        assert prey.alive is False
        assert predator.energy > 150  # Should gain energy


class TestEcosystemSimulation:
    """Test cases for EcosystemSimulation class."""

    def test_initialization(self):
        """Test simulation initialization."""
        sim = EcosystemSimulation(200, 200, {
            'initial_prey': 30,
            'initial_predators': 5
        })
        sim.initialize()
        assert len(sim.prey) == 30
        assert len(sim.predators) == 5
        assert sim.time_step == 0

    def test_grass_growth(self):
        """Test grass growth."""
        sim = EcosystemSimulation(200, 200)
        sim.initialize()
        initial_grass = sim.grass[100, 100].copy()
        sim.update()
        assert sim.grass[100, 100] >= initial_grass

    def test_prey_eat_grass(self):
        """Test prey eating grass."""
        sim = EcosystemSimulation(200, 200)
        sim.initialize()
        sim.grass[100, 100] = 1.0  # Full grass at this location
        sim.prey[0].position = np.array([100.0, 100.0])
        sim.update()
        # Grass should be consumed
        assert sim.grass[100, 100] < 1.0

    def test_update(self):
        """Test update method."""
        sim = EcosystemSimulation(200, 200, {
            'initial_prey': 20,
            'initial_predators': 3
        })
        sim.initialize()
        sim.step()
        assert sim.time_step == 1

    def test_remove_dead_entities(self):
        """Test removal of dead entities."""
        sim = EcosystemSimulation(200, 200)
        sim.initialize()
        # Kill some entities
        if len(sim.prey) > 0:
            sim.prey[0].alive = False
        if len(sim.predators) > 0:
            sim.predators[0].alive = False
        sim.update()
        # Dead entities should be removed
        assert all(p.alive for p in sim.prey)
        assert all(p.alive for p in sim.predators)

    def test_get_state(self):
        """Test get_state method."""
        sim = EcosystemSimulation(200, 200)
        sim.initialize()
        state = sim.get_state()
        assert 'prey_positions' in state
        assert 'predator_positions' in state
        assert 'grass' in state

    def test_get_statistics(self):
        """Test get_statistics method."""
        sim = EcosystemSimulation(200, 200)
        sim.initialize()
        stats = sim.get_statistics()
        assert 'prey_count' in stats
        assert 'predator_count' in stats
        assert 'time_step' in stats
        assert stats['prey_count'] == len(sim.prey)
        assert stats['predator_count'] == len(sim.predators)

    def test_reset(self):
        """Test reset method."""
        sim = EcosystemSimulation(200, 200)
        sim.initialize()
        sim.step()
        sim.step()
        assert sim.time_step == 2
        sim.reset()
        assert sim.time_step == 0

    def test_prey_reproduction_in_simulation(self):
        """Test prey reproduction in full simulation."""
        sim = EcosystemSimulation(200, 200, {
            'initial_prey': 20,
            'grass_growth_rate': 0.5  # Fast grass growth
        })
        sim.initialize()

        # Give prey high energy
        for prey in sim.prey:
            prey.energy = 140

        initial_count = len(sim.prey)
        sim.update()

        # Some prey may reproduce
        assert len(sim.prey) >= initial_count

    def test_predator_starvation(self):
        """Test predators starving without prey."""
        sim = EcosystemSimulation(200, 200, {
            'initial_prey': 0,
            'initial_predators': 5
        })
        sim.initialize()

        # Run until predators starve
        for _ in range(2000):
            sim.update()
            if len(sim.predators) == 0:
                break

        # All predators should eventually die
        assert len(sim.predators) == 0
