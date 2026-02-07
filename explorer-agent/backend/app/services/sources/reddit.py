"""Reddit data source adapter."""

import requests
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class RedditSource:
    """Fetches content from Reddit (no API key needed for public access)."""

    def __init__(self):
        """Initialize Reddit source."""
        self.base_url = "https://www.reddit.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def get_hot_posts(self, subreddit: str = "all", limit: int = 10) -> List[Dict]:
        """Get hot posts from a subreddit."""
        try:
            url = f"{self.base_url}/r/{subreddit}/hot.json"
            params = {'limit': limit}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for post in data.get('data', {}).get('children', []):
                post_data = post.get('data', {})
                results.append({
                    'title': post_data.get('title', ''),
                    'content': post_data.get('selftext', '')[:500],
                    'source': f"https://reddit.com{post_data.get('permalink', '')}",
                    'type': 'reddit',
                    'subreddit': post_data.get('subreddit', ''),
                    'score': post_data.get('score', 0),
                    'comments': post_data.get('num_comments', 0)
                })

            return results

        except Exception as e:
            logger.error(f"Reddit fetch failed: {e}")
            return []

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search Reddit (using multiple subreddits for variety).

        Note: Reddit's search API requires OAuth, so we use hot posts from relevant subreddits.
        """
        # Map query keywords to relevant subreddits
        tech_keywords = ['programming', 'coding', 'developer', 'software', 'tech', 'AI']
        science_keywords = ['science', 'research', 'physics', 'chemistry', 'biology', 'space']
        general_keywords = ['worldnews', 'todayilearned', 'interestingasfuck']

        query_lower = query.lower()

        if any(kw in query_lower for kw in tech_keywords):
            subreddits = ['programming', 'technology', 'MachineLearning', 'compsci']
        elif any(kw in query_lower for kw in science_keywords):
            subreddits = ['science', 'AskScience', 'space', 'Futurology']
        else:
            subreddits = general_keywords

        # Fetch from multiple subreddits
        all_results = []
        for sub in subreddits[:2]:  # Limit to 2 subreddits
            posts = self.get_hot_posts(sub, limit=num_results // 2 + 1)
            all_results.extend(posts)

        return all_results[:num_results]
