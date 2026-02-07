"""Exploration engine - orchestrates the discovery process."""

import random
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import Node, Frontier, ExplorationPath, Edge, LowQualityPool
from app.services.sources import (
    GoogleSearchSource,
    HackerNewsSource,
    ArxivSource,
    RedditSource,
    DuckDuckGoSource,
    GitHubTrendingSource,
    StackOverflowSource,
    PubMedSource
)
from app.services.evaluator import ValueEvaluator
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class ExplorationEngine:
    """Main exploration engine."""

    def __init__(self):
        """Initialize engine with data sources and evaluator."""
        self.google = GoogleSearchSource()
        self.hackernews = HackerNewsSource()
        self.arxiv = ArxivSource()
        self.reddit = RedditSource()
        self.duckduckgo = DuckDuckGoSource()
        self.github = GitHubTrendingSource()
        self.stackoverflow = StackOverflowSource()
        self.pubmed = PubMedSource()
        self.evaluator = ValueEvaluator()

    def explore(self, strategy: str = "mixed", max_iterations: int = 5) -> Dict:
        """
        Run exploration round.

        Args:
            strategy: 'random', 'edge', 'graph', or 'mixed'
            max_iterations: Maximum number of exploration steps

        Returns:
            Dict with exploration results
        """
        db = SessionLocal()
        results = {
            'nodes_created': 0,
            'paths_created': 0,
            'nodes': [],
            'strategy': strategy
        }

        try:
            # Initialize frontier if empty
            self._ensure_frontier_seeds(db)

            # Create exploration path
            current_path = ExplorationPath(
                path=[],
                strategy=strategy,
                started_at=datetime.utcnow()
            )
            db.add(current_path)
            db.commit()

            path_nodes = []
            iteration = 0

            while iteration < max_iterations:
                # Choose strategy for this iteration
                current_strategy = self._choose_strategy(strategy)

                # Get seed from frontier
                seed = self._get_next_seed(db, current_strategy)
                if not seed:
                    logger.warning("Frontier is empty, adding new seeds")
                    self._add_random_seeds(db)
                    seed = self._get_next_seed(db, current_strategy)
                    if not seed:
                        break

                # Explore from seed
                discovered = self._explore_from_seed(seed, current_strategy, db)

                if discovered:
                    # Node already checked in _explore_from_seed, so if we got here it's new
                    # But double-check to be safe (race condition protection)
                    existing = db.query(Node).filter(
                        Node.source == discovered['source']
                    ).first()

                    if existing:
                        logger.info(f"Node already exists (race condition): {discovered['source']}")
                        if seed.attempts is None:
                            seed.attempts = 0
                        seed.attempts += 1
                        db.commit()
                        iteration += 1
                        continue

                    # Extract tags first (needed for both high and low quality paths)
                    tags = self.evaluator.extract_tags(discovered['content'])

                    # Evaluate value
                    existing_nodes = [n.to_dict() for n in db.query(Node).limit(10).all()]
                    value_score = self.evaluator.evaluate(discovered['content'], existing_nodes)

                    if value_score < settings.min_value_score:
                        # Save to low-quality pool for Thinker processing instead of discarding
                        self._save_to_low_quality_pool(db, discovered, value_score, tags)
                        logger.info(f"Node value too low ({value_score:.2f}), saved to pool for Thinker")
                        if seed.attempts is None:
                            seed.attempts = 0
                        seed.attempts += 1
                        db.commit()
                        iteration += 1
                        continue

                    # Create node
                    node = Node(
                        content=discovered['content'],
                        title=discovered.get('title', ''),
                        source=discovered['source'],
                        type=discovered['type'],
                        value_score=value_score,
                        tags=tags
                    )
                    db.add(node)
                    db.flush()  # Get node ID

                    # Add to path
                    path_nodes.append(node.id)

                    # Add new seeds to frontier based on discovery
                    self._add_seeds_from_discovery(db, node, discovered)

                    # Create edges if we have previous nodes in path
                    if path_nodes:
                        prev_node_id = path_nodes[-2] if len(path_nodes) > 1 else None
                        if prev_node_id:
                            edge = Edge(
                                from_node_id=prev_node_id,
                                to_node_id=node.id,
                                relationship='discovered_from',
                                strength=1.0
                            )
                            db.add(edge)

                    results['nodes_created'] += 1
                    results['nodes'].append(node.to_dict())

                    # Update seed
                    if seed.attempts is None:
                        seed.attempts = 0
                    seed.attempts += 1
                    if seed.attempts >= 3:  # Remove after 3 attempts
                        db.delete(seed)

                    logger.info(f"Created node {node.id}: {node.title[:50]}... (score: {value_score:.2f})")

                iteration += 1

            # Complete the path
            current_path.path = path_nodes
            current_path.completed_at = datetime.utcnow()
            current_path.total_value = sum(
                db.query(Node).get(nid).value_score for nid in path_nodes
            )
            results['paths_created'] = 1
            db.commit()

        except Exception as e:
            logger.error(f"Exploration failed: {e}")
            db.rollback()
            raise
        finally:
            db.close()

        logger.info(f"Exploration complete: {results['nodes_created']} nodes, {results['paths_created']} paths")
        return results

    def _ensure_frontier_seeds(self, db: Session):
        """Ensure frontier has initial seeds."""
        count = db.query(Frontier).count()
        if count == 0:
            logger.info("Frontier empty, adding initial seeds")
            self._add_random_seeds(db, count=10)

    def _add_random_seeds(self, db: Session, count: int = 10):
        """Add random seeds to frontier."""
        random_seeds = [
            "machine learning breakthrough 2025",
            "quantum computing applications",
            "sustainable technology innovations",
            "neuroscience latest research",
            "space exploration news",
            "biohacking developments",
            "cryptocurrency trends",
            "AI ethics debate",
            "climate change solutions",
            "longevity research"
        ]

        for seed_text in random_seeds[:count]:
            existing = db.query(Frontier).filter(Frontier.seed == seed_text).first()
            if not existing:
                frontier = Frontier(
                    seed=seed_text,
                    priority=random.uniform(0.5, 1.0)
                )
                db.add(frontier)

        db.commit()

    def _choose_strategy(self, base_strategy: str) -> str:
        """Choose specific strategy for iteration."""
        if base_strategy == "mixed":
            return random.choice(["random", "edge", "graph"])
        return base_strategy

    def _get_next_seed(self, db: Session, strategy: str) -> Optional[Frontier]:
        """Get next seed from frontier based on strategy."""
        if strategy == "random":
            return db.query(Frontier).order_by(Frontier.priority.desc()).first()
        elif strategy == "edge":
            # Prefer seeds with source_node (edge exploration)
            return db.query(Frontier).filter(
                Frontier.source_node_id.isnot(None)
            ).order_by(Frontier.priority.desc()).first()
        else:  # graph
            return db.query(Frontier).order_by(Frontier.priority.desc()).first()

    def _explore_from_seed(self, seed: Frontier, strategy: str, db: Session = None) -> Optional[Dict]:
        """Explore from a seed using ONLY Arxiv (papers only)."""
        query = seed.seed

        try:
            # ONLY use Arxiv for paper search
            # Get multiple results to increase chance of finding new content
            logger.info(f"Searching Arxiv for: {query}")
            results = self.arxiv.search(query, num_results=10)

            if results and len(results) > 0:
                logger.info(f"Found {len(results)} papers")

                # Try each result until we find a non-duplicate one
                for i, result in enumerate(results):
                    # Check if this paper already exists (if db provided)
                    if db:
                        existing = db.query(Node).filter(
                            Node.source == result['source']
                        ).first()
                        if existing:
                            logger.info(f"  Paper {i+1}/{len(results)}: {result.get('title', 'Unknown')[:50]}... (already exists, skipping)")
                            continue

                    # Found a new paper!
                    logger.info(f"  Paper {i+1}/{len(results)}: {result.get('title', 'Unknown')[:50]}... (NEW!)")
                    return result

                logger.info(f"All {len(results)} papers already exist")

        except Exception as e:
            logger.error(f"Arxiv search for '{query}' failed: {e}")

        return None

    def _add_seeds_from_discovery(self, db: Session, node: Node, discovery: Dict):
        """Add new seeds to frontier based on discovery."""
        # Extract keywords from content
        content = discovery.get('content', '')
        title = discovery.get('title', '')
        text = f"{title} {content}"

        # Simple keyword extraction (could be improved with NLP)
        words = text.lower().split()
        keywords = [w for w in words if len(w) > 4 and w.isalpha()]

        # Track seeds added in this session to avoid duplicates
        added_seeds = set()

        # Add top keywords as new seeds
        for keyword in random.sample(keywords[:10], min(3, len(keywords))):
            seed_text = f"{keyword} research"

            # Skip if already added in this session
            if seed_text in added_seeds:
                continue

            existing = db.query(Frontier).filter(Frontier.seed == seed_text).first()
            if not existing:
                frontier = Frontier(
                    seed=seed_text,
                    priority=random.uniform(0.3, 0.8),
                    source_node_id=node.id
                )
                db.add(frontier)
                added_seeds.add(seed_text)

    def _save_to_low_quality_pool(self, db: Session, discovery: Dict, score: float, tags: list):
        """Save low-quality content to pool for Thinker processing."""
        # Check if already in pool
        existing = db.query(LowQualityPool).filter(
            LowQualityPool.source == discovery['source']
        ).first()

        if existing:
            logger.info(f"Content already in low-quality pool: {discovery['source']}")
            return

        # Save to pool
        pool_item = LowQualityPool(
            content=discovery['content'],
            title=discovery.get('title', ''),
            source=discovery['source'],
            type=discovery['type'],
            original_score=score,
            tags=tags,
            processed=False
        )
        db.add(pool_item)
        logger.info(f"Saved to low-quality pool: {discovery.get('title', 'Unknown')[:50]}... (score: {score:.2f})")


# Singleton instance
exploration_engine = ExplorationEngine()

# Alias for compatibility
Explorer = ExplorationEngine
