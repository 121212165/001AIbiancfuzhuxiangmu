"""Celery tasks for exploration."""

from app.tasks.worker import celery_app
from app.services.explorer import exploration_engine
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(name="app.tasks.run_exploration")
def run_exploration_task(strategy: str = "mixed", max_iterations: int = 5):
    """
    Run exploration task.

    Args:
        strategy: Exploration strategy (random/edge/graph/mixed)
        max_iterations: Maximum number of iterations
    """
    logger.info(f"Starting exploration task: strategy={strategy}, max_iterations={max_iterations}")

    try:
        results = exploration_engine.explore(
            strategy=strategy,
            max_iterations=max_iterations
        )

        logger.info(f"Exploration task completed: {results}")
        return results

    except Exception as e:
        logger.error(f"Exploration task failed: {e}")
        raise


@celery_app.task(name="app.tasks.scheduled_exploration")
def scheduled_exploration_task():
    """Run scheduled exploration (called by Celery beat)."""
    logger.info("Running scheduled exploration")

    results = run_exploration_task.apply_async(
        args=["mixed", settings.max_explorations_per_run]
    )

    return {"task_id": results.id, "status": "scheduled"}


@celery_app.task(name="app.tasks.initialize_frontier")
def initialize_frontier_task():
    """Initialize frontier with seeds."""
    from app.db.session import SessionLocal
    from app.services.explorer import ExplorationEngine

    db = SessionLocal()
    try:
        engine = ExplorationEngine()
        engine._ensure_frontier_seeds(db)
        logger.info("Frontier initialized")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Frontier initialization failed: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
