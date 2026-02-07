"""Celery tasks for thinking/processing low-quality content."""

from app.tasks.worker import celery_app
from app.services.thinker import thinking_engine
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(name="app.tasks.run_thinking")
def run_thinking_task(batch_size: int = 10, mode: str = "auto"):
    """
    Run thinking task to process low-quality content.

    Args:
        batch_size: Number of items to process from low-quality pool
        mode: Processing mode (auto/mine_gems/synthesize/discover_connections)
    """
    logger.info(f"Starting thinking task: batch_size={batch_size}, mode={mode}")

    try:
        results = thinking_engine.process_low_quality_pool(
            batch_size=batch_size,
            mode=mode
        )

        logger.info(f"Thinking task completed: {results}")
        return results

    except Exception as e:
        logger.error(f"Thinking task failed: {e}")
        raise


@celery_app.task(name="app.tasks.scheduled_thinking")
def scheduled_thinking_task():
    """
    Run scheduled thinking (called by Celery beat).

    This runs periodically to process accumulated low-quality content.
    """
    logger.info("Running scheduled thinking")

    results = run_thinking_task.apply_async(
        args=[settings.thinking_batch_size, "auto"]
    )

    return {"task_id": results.id, "status": "scheduled"}


@celery_app.task(name="app.tasks.full_cycle")
def full_cycle_task():
    """
    Run a full exploration + thinking cycle.

    This task runs exploration first, then processes the accumulated
    low-quality content with the Thinker.
    """
    from app.tasks.exploration_tasks import run_exploration_task

    logger.info("Starting full cycle: exploration + thinking")

    # Step 1: Run exploration
    exploration_result = run_exploration_task.apply_async(
        args=["mixed", settings.max_explorations_per_run]
    )

    # Wait for exploration to complete
    exploration_result.get(timeout=300)  # 5 minute timeout

    logger.info("Exploration complete, starting thinking")

    # Step 2: Run thinking on accumulated content
    thinking_result = run_thinking_task.apply_async(
        args=[settings.thinking_batch_size, "auto"]
    )

    return {
        "exploration_task_id": exploration_result.id,
        "thinking_task_id": thinking_result.id,
        "status": "full_cycle_started"
    }
