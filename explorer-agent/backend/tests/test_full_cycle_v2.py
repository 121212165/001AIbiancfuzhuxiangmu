"""
Test script for v2.0 full cycle
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.orchestrator_agent import OrchestratorAgent
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_full_cycle():
    """Test complete full cycle"""
    logger.info("=" * 60)
    logger.info("Starting v2.0 Full Cycle Test")
    logger.info("=" * 60)

    # Create orchestrator
    orchestrator = OrchestratorAgent()

    # Run full cycle
    result = orchestrator.run({
        "query": "machine learning",
        "max_results": 5,
        "sources": ["arxiv"]
    })

    # Print results
    logger.info("=" * 60)
    logger.info("Full Cycle Results")
    logger.info("=" * 60)
    logger.info(f"Status: {result['status']}")
    logger.info(f"Metrics: {result['metrics']}")

    if result.get('feedback'):
        logger.info("=" * 60)
        logger.info("Feedback to Explorer:")
        logger.info("=" * 60)
        for i, feedback in enumerate(result['feedback'], 1):
            logger.info(f"{i}. {feedback}")

    if result.get('errors'):
        logger.warning("=" * 60)
        logger.warning("Errors encountered:")
        logger.warning("=" * 60)
        for error in result['errors']:
            logger.warning(f"- {error}")

    logger.info("=" * 60)
    logger.info("Test Complete!")
    logger.info("=" * 60)

    # Save daily report
    if result['status'] in ['success', 'partial']:
        # Get the output data
        output_data = result.get('data', {}).get('output', {})

        if 'daily_report' in output_data:
            os.makedirs('outputs', exist_ok=True)
            report_path = 'outputs/daily_report_v2.md'

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(output_data['daily_report'])

            logger.info(f"Daily report saved to: {report_path}")

    return result


if __name__ == "__main__":
    try:
        result = test_full_cycle()

        if result['status'] == 'success':
            logger.info("✅ Test PASSED")
            sys.exit(0)
        else:
            logger.warning("⚠️ Test completed with errors")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Test FAILED: {str(e)}", exc_info=True)
        sys.exit(1)
