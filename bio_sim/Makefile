.PHONY: help build up down test clean shell run all

# Default target
help:
	@echo "Bio-Sim - Docker commands:"
	@echo ""
	@echo "Build:"
	@echo "  make build       - Build Docker image"
	@echo "  make rebuild     - Rebuild Docker image (no cache)"
	@echo ""
	@echo "Run:"
	@echo "  make up          - Start development container"
	@echo "  make down        - Stop all containers"
	@echo "  make shell       - Enter development container"
	@echo "  make run         - Run the application"
	@echo ""
	@echo "Simulations:"
	@echo "  make boids       - Run Boids simulation"
	@echo "  make ecosystem   - Run ecosystem simulation"
	@echo "  make life        - Run game of life"
	@echo "  make genetic     - Run genetic algorithm"
	@echo ""
	@echo "Development:"
	@echo "  make test        - Run tests"
	@echo "  make format      - Format code"
	@echo "  make lint        - Run linting"
	@echo "  make clean       - Clean up containers and images"
	@echo ""

# Build
build:
	docker-compose build

rebuild:
	docker-compose build --no-cache

# Container management
up:
	docker-compose up -d bio-sim-dev
	@echo "Development container started!"
	@echo "Enter with: make shell"

down:
	docker-compose down

shell:
	docker-compose exec bio-sim-dev /bin/bash

# Run simulations
run:
	docker-compose run --rm bio-sim-dev

boids:
	docker-compose run --rm boids

ecosystem:
	docker-compose run --rm ecosystem

life:
	docker-compose run --rm game-of-life

genetic:
	docker-compose run --rm genetic

# Development
test:
	docker-compose run --rm bio-sim-test

format:
	docker-compose run --rm bio-sim-dev black .
	docker-compose run --rm bio-sim-dev isort .

lint:
	docker-compose run --rm bio-sim-dev flake8 .
	docker-compose run --rm bio-sim-dev mypy core/ simulations/

clean:
	docker-compose down -v
	docker system prune -f

# All
all: build test
	@echo "Build and tests complete!"
