"""HackerNews data source adapter."""

import requests
from typing import List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HackerNewsSource:
    """Fetches content from HackerNews."""

    def __init__(self):
        """Initialize HN source."""
        self.base_url = "https://hacker-news.firebaseio.com/v0"

    def get_front_page(self, num_stories: int = 10) -> List[Dict]:
        """Get stories from HN front page."""
        try:
            # Get top story IDs
            ids_url = f"{self.base_url}/topstories.json"
            response = requests.get(ids_url, timeout=10)
            response.raise_for_status()
            story_ids = response.json()[:num_stories]

            # Fetch story details
            results = []
            for story_id in story_ids:
                story = self._get_story(story_id)
                if story:
                    results.append(story)

            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"HackerNews fetch failed: {e}")
            return []

    def get_new_stories(self, num_stories: int = 10) -> List[Dict]:
        """Get newest stories from HN."""
        try:
            ids_url = f"{self.base_url}/newstories.json"
            response = requests.get(ids_url, timeout=10)
            response.raise_for_status()
            story_ids = response.json()[:num_stories]

            results = []
            for story_id in story_ids:
                story = self._get_story(story_id)
                if story:

                    results.append(story)

            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"HackerNews fetch failed: {e}")
            return []

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search HN Algolia API (more powerful than official API).

        Note: Requires Algolia API, falls back to front page.
        """
        try:
            algolia_url = "http://hn.algolia.com/api/v1/search"
            params = {
                'query': query,
                'hitsPerPage': num_results,
                'tags': 'story'
            }

            response = requests.get(algolia_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for hit in data.get('hits', []):
                results.append({
                    'title': hit.get('title') or hit.get('story_title', ''),
                    'content': hit.get('url', ''),
                    'source': hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                    'type': 'hackernews',
                    'points': hit.get('points', 0),
                    'comments': hit.get('num_comments', 0)
                })

            return results

        except Exception as e:
            logger.warning(f"HN Algolia search failed, using front page: {e}")
            return self.get_front_page(num_results)

    def _get_story(self, story_id: int) -> Dict:
        """Get story details by ID."""
        try:
            url = f"{self.base_url}/item/{story_id}.json"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            item = response.json()

            # Skip jobs, polls, etc.
            if item.get('type') != 'story' or item.get('dead'):
                return None

            # Get comments as content
            content = item.get('text') or item.get('url', '')
            if item.get('descendants'):
                content += f" ({item.get('descendants')} comments)"

            return {
                'title': item.get('title', ''),
                'content': content[:500],  # Limit length
                'source': item.get('url') or f"https://news.ycombinator.com/item?id={story_id}",
                'type': 'hackernews',
                'points': item.get('score', 0),
                'comments': item.get('descendants', 0)
            }

        except Exception as e:
            logger.error(f"Failed to fetch HN story {story_id}: {e}")
            return None
