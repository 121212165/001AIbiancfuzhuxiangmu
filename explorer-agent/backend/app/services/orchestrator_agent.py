"""
Orchestrator Agent - Coordinates all agents in the closed loop
"""
from typing import Dict, List, Any, Optional
from app.agents import AgentProtocol
from app.services.explorer import Explorer
from app.services.evaluator import Evaluator
from app.services.thinker import Thinker
from app.services.organizer_agent import OrganizerAgent
from app.services.outputter_agent import OutputterAgent
import logging

logger = logging.getLogger(__name__)


class OrchestratorAgent(AgentProtocol):
    """
    Orchestrator Agent - Coordinates all agents

    Responsibilities:
    1. Execute agents in sequence: Explorer → Evaluator → Thinker → Organizer → Outputter
    2. Pass data between agents
    3. Handle errors gracefully
    4. Return feedback to Explorer for optimization
    """

    def __init__(self,
                 explorer: Optional[Explorer] = None,
                 evaluator: Optional[Evaluator] = None,
                 thinker: Optional[Thinker] = None,
                 organizer: Optional[OrganizerAgent] = None,
                 outputter: Optional[OutputterAgent] = None):
        """
        Initialize Orchestrator Agent

        Args:
            explorer: Explorer agent
            evaluator: Evaluator agent
            thinker: Thinker agent
            organizer: Organizer agent
            outputter: Outputter agent
        """
        self.explorer = explorer or Explorer()
        self.evaluator = evaluator or Evaluator()
        self.thinker = thinker or Thinker()
        self.organizer = organizer or OrganizerAgent()
        self.outputter = outputter or OutputterAgent()

    def validate_input(self, input_data: Dict) -> bool:
        """Validate input data"""
        # At least query or seeds should be present
        has_query = "query" in input_data and input_data["query"]
        has_seeds = "seeds" in input_data and input_data["seeds"]

        if not has_query and not has_seeds:
            logger.error("Input validation failed: missing both 'query' and 'seeds'")
            return False

        return True

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute complete closed-loop workflow

        Flow:
        Explorer → Evaluator → Thinker → Organizer → Outputter → Feedback to Explorer

        Args:
            input_data: {
                "query": str,          # Search query
                "max_results": int,    # Max results to fetch
                "sources": List[str]   # Data sources to use
            }

        Returns:
            {
                "status": "success" | "partial" | "failed",
                "data": {
                    "exploration": {...},
                    "evaluation": {...},
                    "thinking": {...},
                    "organization": {...},
                    "output": {...}
                },
                "feedback": List[str],
                "metrics": {...},
                "errors": List[str]
            }
        """
        import time
        start_time = time.time()
        errors = []

        # Validate input
        if not self.validate_input(input_data):
            return {
                "status": "failed",
                "data": None,
                "feedback": [],
                "metrics": {},
                "errors": ["Input validation failed"]
            }

        try:
            # ============================================================
            # Step 1: Exploration
            # ============================================================
            logger.info("=" * 60)
            logger.info("STEP 1: Exploration")
            logger.info("=" * 60)

            exploration_result = self.explorer.explore(
                query=input_data.get("query"),
                max_results=input_data.get("max_results", 10),
                sources=input_data.get("sources", ["arxiv"])
            )

            if not exploration_result.get("success", False):
                errors.append("Exploration failed")
                return {
                    "status": "failed",
                    "stage": "exploration",
                    "data": None,
                    "feedback": [],
                    "metrics": {"execution_time": round(time.time() - start_time, 2)},
                    "errors": errors
                }

            discovered_items = exploration_result.get("items", [])
            logger.info(f"Discovered {len(discovered_items)} items")

            # ============================================================
            # Step 2: Evaluation
            # ============================================================
            logger.info("=" * 60)
            logger.info("STEP 2: Evaluation")
            logger.info("=" * 60)

            evaluated_items = []
            low_quality_items = []

            for item in discovered_items:
                evaluation = self.evaluator.evaluate(item)

                if evaluation.get("final_score", 0) >= 0.3:
                    evaluated_items.append(item)
                else:
                    low_quality_items.append(item)

            logger.info(f"High quality: {len(evaluated_items)}, Low quality: {len(low_quality_items)}")

            # ============================================================
            # Step 3: Thinking (if low quality items exist)
            # ============================================================
            logger.info("=" * 60)
            logger.info("STEP 3: Thinking")
            logger.info("=" * 60)

            insights = []
            if low_quality_items:
                thinking_result = self.thinker.process_low_quality_pool(
                    mode="auto",
                    max_items=len(low_quality_items)
                )

                if thinking_result.get("success"):
                    insights = thinking_result.get("insights", [])
                    logger.info(f"Generated {len(insights)} insights from low quality items")
                else:
                    logger.warning("Thinking failed, continuing without insights")
                    errors.append("Thinking failed")
            else:
                logger.info("No low quality items to process")

            # ============================================================
            # Step 4: Organization
            # ============================================================
            logger.info("=" * 60)
            logger.info("STEP 4: Organization")
            logger.info("=" * 60)

            organization_input = {
                "high_quality": evaluated_items,
                "insights": insights
            }

            organization_result = self.organizer.run(organization_input)

            if organization_result["status"] == "failed":
                errors.append("Organization failed")
                # Continue anyway with partial results

            # ============================================================
            # Step 5: Output
            # ============================================================
            logger.info("=" * 60)
            logger.info("STEP 5: Output")
            logger.info("=" * 60)

            output_result = self.outputter.run(organization_result["data"])

            if output_result["status"] == "failed":
                errors.append("Output failed")
                # Continue anyway to get feedback

            # ============================================================
            # Step 6: Feedback
            # ============================================================
            logger.info("=" * 60)
            logger.info("STEP 6: Feedback")
            logger.info("=" * 60)

            feedback = output_result["data"].get("feedback_to_explorer", [])
            logger.info(f"Generated {len(feedback)} feedback items for Explorer")

            execution_time = time.time() - start_time

            return {
                "status": "success" if not errors or output_result["status"] == "success" else "partial",
                "data": {
                    "exploration": {
                        "items_count": len(discovered_items),
                        "sources_used": exploration_result.get("sources_used", [])
                    },
                    "evaluation": {
                        "high_quality_count": len(evaluated_items),
                        "low_quality_count": len(low_quality_items)
                    },
                    "thinking": {
                        "insights_count": len(insights)
                    },
                    "organization": organization_result.get("metrics", {}),
                    "output": output_result.get("metrics", {})
                },
                "feedback": feedback,
                "metrics": {
                    "total_items_discovered": len(discovered_items),
                    "high_quality_items": len(evaluated_items),
                    "insights_generated": len(insights),
                    "execution_time": round(execution_time, 2)
                },
                "errors": errors
            }

        except Exception as e:
            logger.error(f"Orchestrator failed: {str(e)}", exc_info=True)
            errors.append(str(e))

            return {
                "status": "failed",
                "data": None,
                "feedback": [],
                "metrics": {"execution_time": round(time.time() - start_time, 2)},
                "errors": errors
            }

    def get_config(self) -> Dict:
        """Get configuration"""
        return {
            "agent_type": "OrchestratorAgent",
            "agents": {
                "explorer": self.explorer.__class__.__name__,
                "evaluator": self.evaluator.__class__.__name__,
                "thinker": self.thinker.__class__.__name__,
                "organizer": self.organizer.__class__.__name__,
                "outputter": self.outputter.__class__.__name__
            }
        }
