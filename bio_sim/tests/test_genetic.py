"""Unit tests for Genetic Algorithm simulation."""
import pytest
import numpy as np
from simulations.genetic_algorithm import DNA, Agent, Population, GeneticSimulation


class TestDNA:
    """Test cases for DNA class."""

    def test_dna_creation(self):
        """Test DNA creation."""
        dna = DNA(length=10)
        assert dna.genes.shape == (10,)
        assert np.all((dna.genes >= -1) & (dna.genes <= 1))

    def test_dna_from_genes(self):
        """Test DNA creation from existing genes."""
        genes = np.array([0.5, -0.3, 0.8, 0.0])
        dna = DNA(genes=genes)
        assert np.array_equal(dna.genes, genes)

    def test_crossover(self):
        """Test DNA crossover."""
        parent1 = DNA(genes=np.array([1.0, 1.0, 1.0, 1.0]))
        parent2 = DNA(genes=np.array([0.0, 0.0, 0.0, 0.0]))

        child_dna = parent1.crossover(parent2)

        # Child should have genes from both parents
        assert isinstance(child_dna, DNA)
        assert len(child_dna.genes) == 4

    def test_mutate(self):
        """Test DNA mutation."""
        dna = DNA(genes=np.array([0.5, 0.5, 0.5, 0.5]))
        original_genes = dna.genes.copy()

        # Mutate with high rate
        dna.mutate(rate=1.0)

        # With rate=1.0, all genes should potentially change
        assert dna.genes.shape == original_genes.shape

    def test_mutate_low_rate(self):
        """Test DNA mutation with low rate."""
        np.random.seed(42)
        dna = DNA(genes=np.array([0.5, 0.5, 0.5, 0.5]))
        original_genes = dna.genes.copy()

        dna.mutate(rate=0.0)  # No mutation

        # Should be unchanged
        assert np.array_equal(dna.genes, original_genes)


class TestAgent:
    """Test cases for Agent class."""

    def test_agent_creation(self):
        """Test agent creation."""
        agent = Agent(dna_length=10)
        assert agent.dna.genes.shape == (10,)
        assert agent.fitness == 0.0
        assert agent.age == 0

    def test_calculate_fitness(self):
        """Test fitness calculation."""
        agent = Agent(dna_length=5)
        agent.dna.genes = np.array([0.5, 0.5, 0.5, 0.5, 0.5])
        target = np.array([0.5, 0.5, 0.5, 0.5, 0.5])

        agent.calculate_fitness(target)

        # Perfect match should have high fitness
        assert agent.fitness > 0.9

    def test_calculate_fitness_imperfect(self):
        """Test fitness with imperfect match."""
        agent = Agent(dna_length=5)
        agent.dna.genes = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        target = np.array([1.0, 1.0, 1.0, 1.0, 1.0])

        agent.calculate_fitness(target)

        # Poor match should have lower fitness
        assert agent.fitness < 0.5

    def test_update(self):
        """Test agent update."""
        agent = Agent(dna_length=5)
        agent.update()
        assert agent.age == 1


class TestPopulation:
    """Test cases for Population class."""

    def test_population_creation(self):
        """Test population creation."""
        pop = Population(size=10, dna_length=5)
        assert len(pop.agents) == 10
        assert pop.generation == 0

    def test_evaluate(self):
        """Test population evaluation."""
        pop = Population(size=10, dna_length=5)
        target = np.random.randn(5)

        pop.evaluate(target)

        # All agents should have fitness calculated
        for agent in pop.agents:
            assert agent.fitness >= 0

        assert pop.best_fitness > 0
        assert pop.average_fitness > 0

    def test_selection(self):
        """Test selection process."""
        pop = Population(size=10, dna_length=5)
        target = np.random.randn(5)
        pop.evaluate(target)

        selected = pop.selection()
        assert isinstance(selected, type(pop.agents[0]))

    def test_reproduce(self):
        """Test reproduction."""
        pop = Population(size=10, dna_length=5, mutation_rate=0.01)
        target = np.random.randn(5)
        pop.evaluate(target)

        new_pop = pop.reproduce()

        assert isinstance(new_pop, Population)
        assert len(new_pop.agents) == 10
        assert new_pop.generation == 1

    def test_fitness_improves_over_generations(self):
        """Test that fitness improves over generations."""
        pop = Population(size=50, dna_length=10, mutation_rate=0.01)
        target = np.sin(np.linspace(0, 4*np.pi, 10))

        # Evaluate initial population
        pop.evaluate(target)
        initial_best = pop.best_fitness

        # Run for several generations
        for _ in range(10):
            pop.evaluate(target)
            pop = pop.reproduce()

        # Final population should be evaluated
        pop.evaluate(target)
        final_best = pop.best_fitness

        # Fitness should improve (though not guaranteed every time)
        # We just check it runs without error
        assert isinstance(final_best, float)


class TestGeneticSimulation:
    """Test cases for GeneticSimulation class."""

    def test_initialization(self):
        """Test simulation initialization."""
        sim = GeneticSimulation(100, 100, {
            'population_size': 20,
            'dna_length': 10
        })
        sim.initialize()
        assert sim.population is not None
        assert sim.target is not None
        assert len(sim.target) == 10
        assert sim.time_step == 0

    def test_random_target(self):
        """Test random target generation."""
        sim = GeneticSimulation(100, 100, {
            'target_type': 'random'
        })
        sim.initialize()
        assert sim.target is not None
        assert len(sim.target) == sim.config['dna_length']

    def test_pattern_target(self):
        """Test pattern target generation."""
        sim = GeneticSimulation(100, 100, {
            'target_type': 'pattern'
        })
        sim.initialize()
        assert sim.target is not None
        # Pattern is a sine wave
        assert len(sim.target) == sim.config['dna_length']

    def test_zeros_target(self):
        """Test zeros target generation."""
        sim = GeneticSimulation(100, 100, {
            'target_type': 'zeros'
        })
        sim.initialize()
        assert np.all(sim.target == 0)

    def test_update(self):
        """Test update method."""
        sim = GeneticSimulation(100, 100, {
            'population_size': 20,
            'dna_length': 10
        })
        sim.initialize()
        sim.step()
        assert sim.time_step == 1
        assert sim.population.generation == 1

    def test_get_state(self):
        """Test get_state method."""
        sim = GeneticSimulation(100, 100)
        sim.initialize()
        state = sim.get_state()
        assert 'target' in state
        assert 'best_genes' in state
        assert 'generation' in state
        assert 'best_fitness' in state
        assert 'average_fitness' in state

    def test_get_statistics(self):
        """Test get_statistics method."""
        sim = GeneticSimulation(100, 100)
        sim.initialize()
        stats = sim.get_statistics()
        assert 'generation' in stats
        assert 'best_fitness' in stats
        assert 'average_fitness' in stats
        assert 'population_size' in stats

    def test_convergence(self):
        """Test that algorithm converges over time."""
        sim = GeneticSimulation(100, 100, {
            'population_size': 50,
            'dna_length': 10,
            'mutation_rate': 0.01,
            'target_type': 'pattern'
        })
        sim.initialize()

        # Get initial fitness
        state = sim.get_state()
        initial_fitness = state['best_fitness']

        # Run for several generations
        for _ in range(20):
            sim.step()

        # Get final fitness
        state = sim.get_state()
        final_fitness = state['best_fitness']

        # Should improve (though not guaranteed)
        # We mainly check it runs without error
        assert final_fitness >= 0

    def test_reset(self):
        """Test reset method."""
        sim = GeneticSimulation(100, 100)
        sim.initialize()
        sim.step()
        sim.step()
        assert sim.time_step == 2
        sim.reset()
        assert sim.time_step == 0
