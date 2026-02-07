"""DuckDuckGo data source adapter."""

from duckduckgo_search import DDGS
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class DuckDuckGoSource:
    """Fetches search results from DuckDuckGo (no API key needed)."""

    def __init__(self):
        """Initialize DDG source."""
        self.ddgs = DDGS()

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search DuckDuckGo for results."""
        try:
            results = self.ddgs.text(
                query,
                max_results=num_results
            )

            formatted_results = []
            for result in results:
                if isinstance(result, dict):
                    formatted_results.append({
                        'title': result.get('title', ''),
                        'content': result.get('body', ''),
                        'source': result.get('link', ''),
                        'type': 'duckduckgo',
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return []
