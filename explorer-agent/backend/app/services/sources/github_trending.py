"""GitHub Trending data source adapter."""

import requests
from typing import List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GitHubTrendingSource:
    """Fetches trending repositories from GitHub (no API key needed)."""

    def __init__(self):
        """Initialize GitHub Trending source."""
        self.base_url = "https://github.com"
        self.trending_url = f"{self.base_url}/trending"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml'
        }

    def get_trending(self, language: str = "", since: str = "daily", limit: int = 10) -> List[Dict]:
        """
        Get trending repositories.

        Args:
            language: Programming language filter (python, javascript, etc.)
            since: Time period - daily, weekly, monthly
            limit: Number of results
        """
        try:
            # GitHub Trending web scraping
            params = {}
            if language:
                params['language'] = language
            if since == 'weekly':
                params['since'] = 'weekly'
            elif since == 'monthly':
                params['since'] = 'monthly'

            response = requests.get(
                self.trending_url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            # Parse HTML to extract repo information
            # Note: This is a simplified version using GitHub's API alternative
            # For production, consider using GitHub API with authentication
            return self._get_trending_via_search(limit, language)

        except Exception as e:
            logger.error(f"GitHub Trending fetch failed: {e}")
            return []

    def _get_trending_via_search(self, limit: int = 10, language: str = "") -> List[Dict]:
        """
        Alternative: Use GitHub search API (unauthenticated, rate limited).
        """
        try:
            # Search for repos created recently with good stars
            date_str = (datetime.now().replace(day=1)).strftime("%Y-%m-%d")

            query = f"stars:>10 created:>{date_str}"
            if language:
                query += f" language:{language}"

            url = "https://api.github.com/search/repositories"
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': limit
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('full_name', ''),
                    'content': item.get('description', '') or "No description",
                    'source': item.get('html_url', ''),
                    'type': 'github',
                    'stars': item.get('stargazers_count', 0),
                    'language': item.get('language', ''),
                    'topics': item.get('topics', [])
                })

            return results

        except Exception as e:
            logger.warning(f"GitHub search failed: {e}")
            return []

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search GitHub repositories."""
        try:
            url = "https://api.github.com/search/repositories"
            params = {
                'q': f"{query} stars:>10",
                'sort': 'stars',
                'order': 'desc',
                'per_page': num_results
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('full_name', ''),
                    'content': item.get('description', '') or "No description",
                    'source': item.get('html_url', ''),
                    'type': 'github',
                    'stars': item.get('stargazers_count', 0),
                    'language': item.get('language', '')
                })

            return results

        except Exception as e:
            logger.error(f"GitHub search failed: {e}")
            return []
