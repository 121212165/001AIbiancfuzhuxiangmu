"""Google Search data source adapter."""

import requests
from typing import List, Dict
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class GoogleSearchSource:
    """Fetches content from Google Search API."""

    def __init__(self):
        """Initialize Google Search source."""
        self.api_key = settings.google_api_key
        self.search_engine_id = settings.google_search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search Google for content.

        Returns list of dictionaries with:
        - title: str
        - content: str (snippet)
        - source: str (url)
        - type: str ("article")
        """
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google Search API credentials not configured")
            return []

        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(num_results, 10),
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'content': item.get('snippet', ''),
                    'source': item.get('link', ''),
                    'type': 'article'
                })

            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"Google Search failed: {e}")
            return []

    def is_configured(self) -> bool:
        """Check if Google Search is properly configured."""
        return bool(self.api_key and self.search_engine_id)
