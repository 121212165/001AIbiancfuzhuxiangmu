"""FastAPI application."""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.tasks.exploration_tasks import run_exploration_task, initialize_frontier_task
from app.models import Node, ExplorationPath, Frontier, LowQualityPool, Insight, ThinkingProcess
from app.core.config import get_settings
from app.services.thinker import thinking_engine
from app.api.v2 import router as v2_router
from typing import List
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title="Explorer Agent API",
    description="Information exploration agent for breaking filter bubbles",
    version="2.0"
)

# Include v2 API router
app.include_router(v2_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting Explorer Agent API")
    # Initialize frontier
    try:
        initialize_frontier_task.delay()
    except Exception as e:
        logger.warning(f"Could not initialize frontier on startup: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Explorer Agent API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/v1/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get exploration statistics including Thinker system."""
    total_nodes = db.query(Node).count()
    total_paths = db.query(ExplorationPath).count()
    frontier_count = db.query(Frontier).count()

    # Thinker statistics
    low_quality_count = db.query(LowQualityPool).count()
    low_quality_unprocessed = db.query(LowQualityPool).filter_by(processed=False).count()
    insights_count = db.query(Insight).count()
    thinking_processes_count = db.query(ThinkingProcess).count()

    # Calculate average value scores
    nodes = db.query(Node).all()
    avg_value = sum(n.value_score for n in nodes) / len(nodes) if nodes else 0

    insights = db.query(Insight).all()
    avg_insight_value = sum(i.value_score for i in insights) / len(insights) if insights else 0

    return {
        "total_nodes": total_nodes,
        "total_paths": total_paths,
        "frontier_count": frontier_count,
        "avg_value_score": avg_value,
        # Thinker stats
        "low_quality_pool_size": low_quality_count,
        "low_quality_unprocessed": low_quality_unprocessed,
        "total_insights": insights_count,
        "thinking_sessions": thinking_processes_count,
        "avg_insight_value": avg_insight_value
    }


@app.get("/api/v1/nodes")
async def get_nodes(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """Get discovered nodes."""
    nodes = db.query(Node).order_by(Node.discovered_at.desc()).offset(offset).limit(limit).all()
    return {
        "nodes": [node.to_dict() for node in nodes],
        "count": len(nodes),
        "total": db.query(Node).count()
    }


@app.get("/api/v1/nodes/{node_id}")
async def get_node(node_id: int, db: Session = Depends(get_db)):
    """Get specific node."""
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node.to_dict()


@app.get("/api/v1/paths")
async def get_paths(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    """Get exploration paths."""
    paths = db.query(ExplorationPath).order_by(
        ExplorationPath.started_at.desc()
    ).offset(offset).limit(limit).all()

    # Enrich with node data
    result = []
    for path in paths:
        path_dict = path.to_dict()
        # Get nodes in path
        nodes = db.query(Node).filter(Node.id.in_(path.path)).all()
        path_dict["nodes"] = [node.to_dict() for node in nodes]
        result.append(path_dict)

    return {
        "paths": result,
        "count": len(result),
        "total": db.query(ExplorationPath).count()
    }


@app.get("/api/v1/frontier")
async def get_frontier(limit: int = 50, db: Session = Depends(get_db)):
    """Get frontier queue."""
    frontier = db.query(Frontier).order_by(
        Frontier.priority.desc()
    ).limit(limit).all()

    return {
        "seeds": [f.to_dict() for f in frontier],
        "count": len(frontier),
        "total": db.query(Frontier).count()
    }


@app.post("/api/v1/explore/start")
async def start_exploration(
    background_tasks: BackgroundTasks,
    strategy: str = "mixed",
    max_iterations: int = 5
):
    """
    Trigger exploration round.

    Args:
        strategy: Exploration strategy (random/edge/graph/mixed)
        max_iterations: Maximum iterations
    """
    task = run_exploration_task.apply_async(
        args=[strategy, max_iterations]
    )

    return {
        "message": "Exploration started",
        "task_id": task.id,
        "strategy": strategy,
        "max_iterations": max_iterations
    }


@app.post("/api/v1/explore/from_seed/{seed_id}")
async def explore_from_seed(
    seed_id: int,
    max_iterations: int = 3,
    db: Session = Depends(get_db)
):
    """
    Explore from a specific seed.

    Args:
        seed_id: ID of the frontier seed to explore from
        max_iterations: Maximum iterations
    """
    seed = db.query(Frontier).filter(Frontier.id == seed_id).first()
    if not seed:
        raise HTTPException(status_code=404, detail="Seed not found")

    # Trigger exploration focused on this seed
    task = run_exploration_task.apply_async(
        args=["graph", max_iterations]
    )

    return {
        "message": "Exploration started from seed",
        "task_id": task.id,
        "seed": seed.seed,
        "seed_id": seed_id
    }


@app.post("/api/v1/frontier/clear")
async def clear_frontier(db: Session = Depends(get_db)):
    """Clear all seeds from frontier."""
    count = db.query(Frontier).count()
    db.query(Frontier).delete()
    db.commit()

    return {
        "message": "Frontier cleared",
        "deleted_count": count
    }


@app.post("/api/v1/frontier/add")
async def add_seed(seed: str, priority: float = 1.0, db: Session = Depends(get_db)):
    """Add new seed to frontier."""
    existing = db.query(Frontier).filter(Frontier.seed == seed).first()
    if existing:
        return {"message": "Seed already exists", "id": existing.id}

    frontier = Frontier(seed=seed, priority=priority)
    db.add(frontier)
    db.commit()

    return {"message": "Seed added", "id": frontier.id}


@app.delete("/api/v1/frontier/{seed_id}")
async def remove_seed(seed_id: int, db: Session = Depends(get_db)):
    """Remove seed from frontier."""
    seed = db.query(Frontier).filter(Frontier.id == seed_id).first()
    if not seed:
        raise HTTPException(status_code=404, detail="Seed not found")

    db.delete(seed)
    db.commit()

    return {"message": "Seed removed"}


# ============ Thinker System Endpoints ============

@app.get("/api/v1/thinker/low_quality_pool")
async def get_low_quality_pool(
    limit: int = 50,
    processed_only: bool = False,
    unprocessed_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get low quality content pool."""
    query = db.query(LowQualityPool)

    if processed_only:
        query = query.filter_by(processed=True)
    elif unprocessed_only:
        query = query.filter_by(processed=False)

    items = query.order_by(LowQualityPool.discovered_at.desc()).offset(0).limit(limit).all()

    return {
        "items": [item.to_dict() for item in items],
        "count": len(items),
        "total": db.query(LowQualityPool).count(),
        "unprocessed": db.query(LowQualityPool).filter_by(processed=False).count()
    }


@app.get("/api/v1/thinker/insights")
async def get_insights(
    limit: int = 50,
    insight_type: str = None,
    db: Session = Depends(get_db)
):
    """Get insights extracted by Thinker."""
    query = db.query(Insight)

    if insight_type:
        query = query.filter_by(insight_type=insight_type)

    insights = query.order_by(Insight.created_at.desc()).offset(0).limit(limit).all()

    return {
        "insights": [insight.to_dict() for insight in insights],
        "count": len(insights),
        "total": db.query(Insight).count()
    }


@app.get("/api/v1/thinker/processes")
async def get_thinking_processes(
    limit: int = 50,
    session_type: str = None,
    db: Session = Depends(get_db)
):
    """Get thinking process records."""
    query = db.query(ThinkingProcess)

    if session_type:
        query = query.filter_by(session_type=session_type)

    processes = query.order_by(ThinkingProcess.created_at.desc()).offset(0).limit(limit).all()

    return {
        "processes": [process.to_dict() for process in processes],
        "count": len(processes),
        "total": db.query(ThinkingProcess).count()
    }


@app.post("/api/v1/thinker/process")
async def trigger_thinking(
    background_tasks: BackgroundTasks,
    batch_size: int = 10,
    mode: str = "auto"
):
    """
    Trigger Thinker processing.

    Args:
        batch_size: Number of low-quality items to process
        mode: Processing mode (auto/mine_gems/synthesize/discover_connections)
    """
    from app.tasks.thinking_tasks import run_thinking_task

    task = run_thinking_task.apply_async(
        args=[batch_size, mode]
    )

    return {
        "message": "Thinking process started",
        "task_id": task.id,
        "batch_size": batch_size,
        "mode": mode
    }


@app.get("/api/v1/thinker/status/{task_id}")
async def get_thinking_status(task_id: str):
    """Get status of thinking task."""
    from celery.result import AsyncResult
    from app.tasks.thinking_tasks import run_thinking_task

    task = AsyncResult(task_id, task=run_thinking_task)

    if task.state == 'PENDING':
        response = {"state": task.state, "status": "Pending..."}
    elif task.state != 'FAILURE':
        response = {
            "state": task.state,
            "result": task.result if task.ready() else None
        }
    else:
        response = {
            "state": task.state,
            "status": str(task.info)
        }

    return response


@app.delete("/api/v1/thinker/low_quality_pool/clear")
async def clear_low_quality_pool(
    processed_only: bool = True,
    db: Session = Depends(get_db)
):
    """Clear items from low quality pool."""
    query = db.query(LowQualityPool)

    if processed_only:
        query = query.filter_by(processed=True)

    count = query.count()
    query.delete()
    db.commit()

    return {
        "message": f"Cleared {count} items from low quality pool",
        "deleted_count": count
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
