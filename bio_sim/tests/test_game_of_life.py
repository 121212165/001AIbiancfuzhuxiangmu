"""Unit tests for Game of Life simulation."""
import pytest
import numpy as np
from simulations.game_of_life import GameOfLife


class TestGameOfLife:
    """Test cases for GameOfLife class."""

    def test_initialization(self):
        """Test simulation initialization."""
        sim = GameOfLife(50, 50, {"density": 0.5})
        sim.initialize()
        assert sim.width == 50
        assert sim.height == 50
        assert sim.grid.shape == (50, 50)

    def test_count_neighbors_center(self):
        """Test counting neighbors for a center cell."""
        sim = GameOfLife(50, 50)
        sim.initialize()
        sim.grid[25:28, 25:28] = np.ones((3, 3))  # 3x3 block
        assert sim.count_neighbors(26, 26) == 8

    def test_count_neighbors_corner(self):
        """Test counting neighbors for a corner cell."""
        sim = GameOfLife(50, 50)
        sim.initialize()
        sim.grid[0, 0] = 1
        sim.grid[0, 1] = 1
        sim.grid[1, 0] = 1
        assert sim.count_neighbors(0, 0) == 2

    def test_blinker_pattern(self):
        """Test blinker oscillator pattern."""
        sim = GameOfLife(10, 10)
        sim.initialize()

        # Create a blinker (vertical line of 3)
        sim.grid[4:7, 5] = 1

        # After one update, it should be horizontal
        sim.update()
        assert sim.grid[5, 4:7].sum() == 3  # Horizontal

        # After another update, it should be vertical again
        sim.update()
        assert sim.grid[4:7, 5].sum() == 3  # Vertical

    def test_still_life_block(self):
        """Test block still life pattern."""
        sim = GameOfLife(10, 10)
        sim.initialize()

        # Create a 2x2 block
        sim.grid[5:7, 5:7] = 1

        # Should remain unchanged
        initial_state = sim.grid.copy()
        sim.update()
        assert np.array_equal(sim.grid, initial_state)

    def test_set_pattern(self):
        """Test setting a pattern."""
        sim = GameOfLife(10, 10)
        sim.initialize()

        pattern = sim.get_glider_pattern()
        sim.set_pattern(pattern, 2, 2)

        assert pattern.shape == (3, 3)
        assert np.array_equal(sim.grid[2:5, 2:5], pattern)

    def test_get_statistics(self):
        """Test get_statistics method."""
        sim = GameOfLife(50, 50)
        sim.initialize()
        stats = sim.get_statistics()
        assert "live_cells" in stats
        assert "time_step" in stats
        assert "density" in stats
        assert stats["time_step"] == 0
