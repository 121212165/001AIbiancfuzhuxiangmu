"""
API endpoints v2 - 5-Agent System
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

from app.services.orchestrator_agent import OrchestratorAgent
from app.services.organizer_agent import OrganizerAgent
from app.services.outputter_agent import OutputterAgent

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================
# Request/Response Models
# ============================================================

class FullCycleRequest(BaseModel):
    """Request for full cycle execution"""
    query: str
    max_results: int = 10
    sources: List[str] = ["arxiv"]


class OrganizerRequest(BaseModel):
    """Request for organizer agent"""
    high_quality: List[Dict[str, Any]]
    insights: List[Dict[str, Any]]


class OutputterRequest(BaseModel):
    """Request for outputter agent"""
    knowledge_graph: Dict[str, Any]
    topics: Dict[str, Any]
    timeline: Dict[str, Any]
    trends: Dict[str, Any]
    questions: Dict[str, Any]


# ============================================================
# Orchestrator Endpoints
# ============================================================

@router.post("/orchestrator/run", response_model=Dict[str, Any])
async def run_orchestrator(request: FullCycleRequest, background_tasks: BackgroundTasks):
    """
    Run complete closed-loop workflow

    Executes: Explorer → Evaluator → Thinker → Organizer → Outputter → Feedback
    """
    try:
        orchestrator = OrchestratorAgent()

        result = orchestrator.run({
            "query": request.query,
            "max_results": request.max_results,
            "sources": request.sources
        })

        return result

    except Exception as e:
        logger.error(f"Orchestrator endpoint failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orchestrator/run-async")
async def run_orchestrator_async(request: FullCycleRequest, background_tasks: BackgroundTasks):
    """
    Run orchestrator in background
    """
    def run_task():
        try:
            orchestrator = OrchestratorAgent()
            result = orchestrator.run({
                "query": request.query,
                "max_results": request.max_results,
                "sources": request.sources
            })
            logger.info(f"Background orchestrator completed: {result['status']}")
        except Exception as e:
            logger.error(f"Background orchestrator failed: {str(e)}")

    background_tasks.add_task(run_task)

    return {
        "status": "started",
        "message": "Orchestrator running in background"
    }


# ============================================================
# Organizer Endpoints
# ============================================================

@router.post("/organizer/run")
async def run_organizer(request: OrganizerRequest):
    """
    Run organizer agent
    """
    try:
        organizer = OrganizerAgent()

        # Convert dicts to objects (simplified for MVP)
        from app.models.node import Node
        from app.models.insight import Insight

        high_quality = [Node(**item) for item in request.high_quality]
        insights = [Insight(**item) for item in request.insights]

        result = organizer.run({
            "high_quality": high_quality,
            "insights": insights
        })

        return result

    except Exception as e:
        logger.error(f"Organizer endpoint failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Outputter Endpoints
# ============================================================

@router.post("/outputter/run")
async def run_outputter(request: OutputterRequest):
    """
    Run outputter agent
    """
    try:
        outputter = OutputterAgent()

        result = outputter.run({
            "knowledge_graph": request.knowledge_graph,
            "topics": request.topics,
            "timeline": request.timeline,
            "trends": request.trends,
            "questions": request.questions
        })

        return result

    except Exception as e:
        logger.error(f"Outputter endpoint failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/outputter/reports")
async def get_reports(limit: int = 10):
    """
    Get generated reports
    """
    try:
        from app.db.database import get_db
        from app.models.outputter import GeneratedReport
        from sqlalchemy import desc

        db = next(get_db())

        reports = db.query(GeneratedReport).order_by(
            desc(GeneratedReport.created_at)
        ).limit(limit).all()

        return {
            "reports": [
                {
                    "id": r.id,
                    "type": r.report_type,
                    "title": r.title,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "format": r.format
                }
                for r in reports
            ]
        }

    except Exception as e:
        logger.error(f"Get reports failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Health & Info
# ============================================================

@router.get("/health")
async def health_check():
    """Health check for v2 API"""
    return {
        "status": "healthy",
        "version": "2.0",
        "agents": {
            "orchestrator": "ready",
            "organizer": "ready",
            "outputter": "ready"
        }
    }


@router.get("/info")
async def get_info():
    """Get information about v2.0 system"""
    return {
        "version": "2.0",
        "description": "5-Agent Closed-Loop Knowledge Discovery System",
        "agents": [
            "Explorer - Discovers content from multiple sources",
            "Evaluator - Evaluates content quality using AI",
            "Thinker - Extracts insights from low-quality content",
            "Organizer - Builds knowledge graph and clusters topics",
            "Outputter - Generates reports and visualizations"
        ],
        "features": [
            "Automated closed-loop workflow",
            "Knowledge graph construction",
            "Topic clustering",
            "Timeline analysis",
            "Trend identification",
            "Research question discovery",
            "Daily/weekly reports",
            "Interactive visualizations",
            "Feedback for continuous optimization"
        ]
    }
