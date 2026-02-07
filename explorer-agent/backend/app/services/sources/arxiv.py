"""Arxiv data source adapter."""

import arxiv
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class ArxivSource:
    """Fetches papers from Arxiv."""

    def __init__(self):
        """Initialize Arxiv source."""
        self.client = arxiv.Client(
            page_size=10,
            delay_seconds=3.0,
            num_retries=3
        )

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search Arxiv for papers.

        Returns list of dictionaries with paper metadata.
        """
        try:
            search = arxiv.Search(
                query=query,
                max_results=num_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )

            results = []
            for result in self.client.results(search):
                # Get first author
                authors = ', '.join([a.name for a in result.authors[:3]])
                if len(result.authors) > 3:
                    authors += ' et al.'

                # Build summary
                content = f"{result.summary[:500]}...\n\nAuthors: {authors}"

                results.append({
                    'title': result.title,
                    'content': content,
                    'source': result.entry_id,
                    'type': 'paper',
                    'published': result.published.strftime('%Y-%m-%d'),
                    'categories': result.categories,
                    'pdf_url': result.pdf_url
                })

            return results

        except Exception as e:
            logger.error(f"Arxiv search failed: {e}")
            return []

    def get_recent_papers(self, category: str = "cs.AI", num_results: int = 5) -> List[Dict]:
        """
        Get recent papers from a category.

        Common categories:
        - cs.AI: Artificial Intelligence
        - cs.LG: Machine Learning
        - cs.CL: Computation and Language (NLP)
        - cs.CR: Cryptography and Security
        - q-bio: Quantitative Biology
        """
        query = f"cat:{category}"
        return self.search(query, num_results)
