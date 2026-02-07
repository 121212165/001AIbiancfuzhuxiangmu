"""Data source adapters."""

from .google_search import GoogleSearchSource
from .hackernews import HackerNewsSource
from .arxiv import ArxivSource
from .reddit import RedditSource
from .duckduckgo import DuckDuckGoSource
from .github_trending import GitHubTrendingSource
from .stackoverflow import StackOverflowSource
from .pubmed import PubMedSource

__all__ = [
    "GoogleSearchSource",
    "HackerNewsSource",
    "ArxivSource",
    "RedditSource",
    "DuckDuckGoSource",
    "GitHubTrendingSource",
    "StackOverflowSource",
    "PubMedSource"
]
