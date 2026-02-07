"""
Outputter Agent - Report Generator
"""
from typing import Dict, List, Any, Optional
from app.agents import AgentProtocol
from app.services.outputter.report_generator import ReportGenerator
from app.services.outputter.visualization_generator import VisualizationGenerator
from app.services.outputter.feedback_generator import FeedbackGenerator
from app.db.database import get_db
from app.models.outputter import GeneratedReport
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class OutputterAgent(AgentProtocol):
    """
    Outputter Agent - Report Generator

    Responsibilities:
    1. Generate daily/weekly reports
    2. Generate insight briefs
    3. Generate visualizations
    4. Generate feedback for Explorer
    """

    def __init__(self,
                 report_generator: Optional[ReportGenerator] = None,
                 visualization_generator: Optional[VisualizationGenerator] = None,
                 feedback_generator: Optional[FeedbackGenerator] = None,
                 output_dir: str = "outputs"):
        """
        Initialize Outputter Agent

        Args:
            report_generator: Report generator
            visualization_generator: Visualization generator
            feedback_generator: Feedback generator
            output_dir: Output directory for files
        """
        self.report_generator = report_generator or ReportGenerator()
        self.visualization_generator = visualization_generator or VisualizationGenerator()
        self.feedback_generator = feedback_generator or FeedbackGenerator()
        self.output_dir = output_dir

    def validate_input(self, input_data: Dict) -> bool:
        """Validate input data"""
        required_keys = ['knowledge_graph', 'topics', 'timeline', 'trends', 'questions']

        for key in required_keys:
            if key not in input_data:
                logger.error(f"Missing required key: {key}")
                return False

        return True

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute output process

        Args:
            input_data: Organizer output data

        Returns:
            {
                "status": "success" | "partial" | "failed",
                "data": {
                    "daily_report": str,
                    "weekly_digest": str,
                    "insight_briefs": List[str],
                    "visualizations": Dict,
                    "feedback_to_explorer": List[str]
                },
                "metrics": {...},
                "errors": [...]
            }
        """
        import time
        start_time = time.time()
        errors = []

        if not self.validate_input(input_data):
            return {
                "status": "failed",
                "data": None,
                "metrics": {},
                "errors": ["Input validation failed"]
            }

        try:
            # 1. Generate daily report
            logger.info("Step 1: Generating daily report...")
            daily_report = self.report_generator.generate_daily_report(input_data)

            # 2. Generate weekly digest
            logger.info("Step 2: Generating weekly digest...")
            weekly_digest = self.report_generator.generate_weekly_digest(input_data)

            # 3. Generate insight briefs
            logger.info("Step 3: Generating insight briefs...")
            insight_briefs = self.report_generator.generate_insight_briefs(input_data)

            # 4. Generate visualizations
            logger.info("Step 4: Generating visualizations...")
            visualizations = self.visualization_generator.generate_all(input_data, self.output_dir)

            # 5. Generate feedback
            logger.info("Step 5: Generating feedback...")
            feedback = self.feedback_generator.generate_feedback(input_data)

            execution_time = time.time() - start_time

            # 6. Save reports to database
            self._save_reports(daily_report, weekly_digest, feedback)

            return {
                "status": "success",
                "data": {
                    "daily_report": daily_report,
                    "weekly_digest": weekly_digest,
                    "insight_briefs": insight_briefs,
                    "visualizations": visualizations,
                    "feedback_to_explorer": feedback
                },
                "metrics": {
                    "reports_generated": 3,
                    "visualizations_created": len(visualizations),
                    "insight_briefs_created": len(insight_briefs),
                    "feedback_items": len(feedback),
                    "execution_time": round(execution_time, 2)
                },
                "errors": errors
            }

        except Exception as e:
            logger.error(f"Outputter agent failed: {str(e)}", exc_info=True)
            errors.append(str(e))

            return {
                "status": "failed",
                "data": None,
                "metrics": {"execution_time": round(time.time() - start_time, 2)},
                "errors": errors
            }

    def _save_reports(self, daily_report: str, weekly_digest: str, feedback: List[str]):
        """Save reports to database"""
        db = next(get_db())

        try:
            # Save daily report
            daily = GeneratedReport(
                report_type="daily",
                title=f"Daily Report - {self._get_today_date()}",
                content=daily_report,
                format="markdown",
                feedback_to_explorer={"suggestions": feedback}
            )
            db.add(daily)

            # Save weekly digest
            weekly = GeneratedReport(
                report_type="weekly",
                title=f"Weekly Digest - Week {self._get_week_number()}",
                content=weekly_digest,
                format="markdown",
                feedback_to_explorer={"suggestions": feedback}
            )
            db.add(weekly)

            db.commit()
            logger.info("Reports saved to database")

        except Exception as e:
            logger.error(f"Failed to save reports: {str(e)}")
            db.rollback()
        finally:
            db.close()

    def _get_today_date(self) -> str:
        """Get today's date as string"""
        from datetime import date
        return date.today().isoformat()

    def _get_week_number(self) -> int:
        """Get current week number"""
        from datetime import date
        return date.today().isocalendar()[1]

    def get_config(self) -> Dict:
        """Get configuration"""
        return {
            "agent_type": "OutputterAgent",
            "output_dir": self.output_dir,
            "components": {
                "report_generator": self.report_generator.__class__.__name__,
                "visualization_generator": self.visualization_generator.__class__.__name__,
                "feedback_generator": self.feedback_generator.__class__.__name__
            }
        }
