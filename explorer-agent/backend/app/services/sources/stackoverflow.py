"""Stack Overflow data source adapter."""

import requests
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class StackOverflowSource:
    """Fetches content from Stack Overflow (no API key needed for basic access)."""

    def __init__(self):
        """Initialize Stack Overflow source."""
        self.api_url = "https://api.stackexchange.com/2.3"

    def get_hot_questions(self, tag: str = "", limit: int = 10) -> List[Dict]:
        """Get hot questions from Stack Overflow."""
        try:
            params = {
                'order': 'desc',
                'sort': 'hot',
                'site': 'stackoverflow',
                'pagesize': limit,
                'filter': '!-*f(6rR5T5B'  # Include body and answers
            }

            if tag:
                params['tagged'] = tag

            response = requests.get(f"{self.api_url}/questions", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('items', []):
                # Get tags as string
                tags = ', '.join(item.get('tags', [])[:5])

                results.append({
                    'title': item.get('title', ''),
                    'content': item.get('body_markdown', '')[:500] if item.get('body_markdown') else item.get('title', ''),
                    'source': item.get('link', ''),
                    'type': 'stackoverflow',
                    'score': item.get('score', 0),
                    'answers': item.get('answer_count', 0),
                    'views': item.get('view_count', 0),
                    'tags': tags
                })

            return results

        except Exception as e:
            logger.error(f"Stack Overflow fetch failed: {e}")
            return []

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search Stack Overflow for questions."""
        try:
            params = {
                'order': 'desc',
                'sort': 'relevance',
                'intitle': query,
                'site': 'stackoverflow',
                'pagesize': num_results
            }

            response = requests.get(f"{self.api_url}/search/advanced", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('items', []):
                tags = ', '.join(item.get('tags', [])[:5])

                results.append({
                    'title': item.get('title', ''),
                    'content': item.get('excerpt', '')[:500] if item.get('excerpt') else item.get('title', ''),
                    'source': item.get('link', ''),
                    'type': 'stackoverflow',
                    'score': item.get('score', 0),
                    'answers': item.get('answer_count', 0),
                    'tags': tags
                })

            return results

        except Exception as e:
            logger.error(f"Stack Overflow search failed: {e}")
            # Fallback to hot questions
            return self.get_hot_questions(limit=num_results)
