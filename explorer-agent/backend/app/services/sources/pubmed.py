"""PubMed data source adapter."""

import requests
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class PubMedSource:
    """Fetches research papers from PubMed (no API key needed)."""

    def __init__(self):
        """Initialize PubMed source."""
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = "explorer-agent@example.com"  # Required by PubMed

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search PubMed for research papers."""
        try:
            # Step 1: Search for paper IDs
            search_url = f"{self.base_url}/esearch.fcgi"
            search_params = {
                'db': 'pubmed',
                'term': query,
                'retmax': num_results,
                'retmode': 'json',
                'sort': 'relevance',
                'email': self.email
            }

            response = requests.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            search_data = response.json()

            id_list = search_data.get('esearchresult', {}).get('idlist', [])
            if not id_list:
                logger.warning(f"No PubMed results for: {query}")
                return []

            # Step 2: Fetch summaries for each ID
            summary_url = f"{self.base_url}/esummary.fcgi"
            summary_params = {
                'db': 'pubmed',
                'id': ','.join(id_list),
                'retmode': 'json',
                'email': self.email
            }

            response = requests.get(summary_url, params=summary_params, timeout=10)
            response.raise_for_status()
            summary_data = response.json()

            results = []
            for paper_id in id_list:
                paper_info = summary_data.get('result', {}).get(paper_id, {})

                # Get authors
                authors = paper_info.get('authors', [])
                author_names = [a.get('name', '') for a in authors[:3]] if authors else []
                author_str = ', '.join(author_names)

                # Get publication date
                pubdate = paper_info.get('pubdate', 'Unknown date')

                results.append({
                    'title': paper_info.get('title', ''),
                    'content': f"Authors: {author_str}\nPublished: {pubdate}\nJournal: {paper_info.get('source', '')}",
                    'source': f"https://pubmed.ncbi.nlm.nih.gov/{paper_id}/",
                    'type': 'pubmed',
                    'authors': author_str,
                    'journal': paper_info.get('source', ''),
                    'pubdate': pubdate
                })

            return results

        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            return []
