"""
Agent Protocol - Base interface for all agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class AgentProtocol(ABC):
    """
    Base protocol that all agents must implement

    This ensures consistent interface across all agents
    """

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent logic

        Args:
            input_data: Input data for the agent

        Returns:
            Dict containing:
                - status: "success" | "partial" | "failed"
                - data: Processing results
                - metrics: Performance metrics
                - errors: Error list (if any)
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: Dict) -> bool:
        """
        Validate input data

        Args:
            input_data: Input data to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    def get_config(self) -> Dict:
        """
        Get current configuration

        Returns:
            Dict with configuration details
        """
        return {
            "agent_type": self.__class__.__name__,
        }

    def get_metrics(self) -> Dict:
        """
        Get runtime metrics

        Returns:
            Dict with performance metrics
        """
        return {
            "total_runs": getattr(self, '_runs', 0),
            "success_rate": getattr(self, '_success_rate', 0.0),
            "avg_time": getattr(self, '_avg_time', 0.0)
        }
