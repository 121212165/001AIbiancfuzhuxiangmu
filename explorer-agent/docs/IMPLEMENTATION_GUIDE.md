# Explorer Agent v2.0 - 实施指南

**版本**: 2.0
**创建日期**: 2025-12-29
**目标**: 从现有3-Agent系统升级到5-Agent闭环自动化系统

---

## 📋 目录

1. [实施概览](#实施概览)
2. [环境准备](#环境准备)
3. [Week 1-2: Organizer Agent实施](#week-1-2-organizer-agent实施)
4. [Week 3-4: Outputter Agent实施](#week-3-4-outputter-agent实施)
5. [Week 5: 闭环与编排](#week-5-闭环与编排)
6. [Week 6-8: 优化与测试](#week-6-8-优化与测试)
7. [部署指南](#部署指南)
8. [常见问题](#常见问题)

---

## 实施概览

### 系统升级路径

```
当前系统 (v1.x):
Explorer → Evaluator → (手动查看) → Thinker (可选)

目标系统 (v2.0):
Explorer → Evaluator → Thinker → Organizer → Outputter → 反馈到 Explorer
   ↓                                                      ↑
完整自动化循环，无需人工干预 ─────────────────────────────────┘
```

### 实施阶段总览

| 阶段 | 时间 | 目标 | 交付物 |
|------|------|------|--------|
| Phase 1 | Week 1-2 | Organizer Agent | 知识图谱、主题聚类、时间线分析 |
| Phase 2 | Week 3-4 | Outputter Agent | 报告生成、可视化、反馈机制 |
| Phase 3 | Week 5 | 闭环编排 | Orchestrator、自动化流程 |
| Phase 4 | Week 6-8 | 测试优化 | 单元测试、性能优化、文档 |

---

## 环境准备

### 1. 新增Python依赖

创建 `requirements-v2.txt`:

```txt
# 现有依赖 (保持)
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
celery==5.3.4
redis==5.0.1
pydantic==2.5.2
pydantic-settings==2.1.0
httpx==0.25.2
python-dotenv==1.0.0
arxiv==2.1.0
 beautifulsoup4==4.12.2
lxml==5.1.0
streamlit==1.29.0
alembic==1.13.1

# v2.0 新增依赖
sentence-transformers==2.2.2
umap-learn==0.5.5
hdbscan==0.8.33
networkx==3.2.1
pyvis==0.3.2
plotly==5.18.0
jinja2==3.1.2
scikit-learn==1.3.2
numpy==1.24.3
pandas==2.1.4
jieba==0.42.1
spacy==3.7.2
```

### 2. 安装命令

```bash
# 在项目根目录
cd explorer-agent

# 安装新依赖
pip install -r requirements-v2.txt

# 下载spaCy中文模型
python -m spacy download zh_core_web_sm

# 下载sentence-transformers模型 (首次运行会自动下载)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### 3. Docker更新

更新 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: explorer_backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://explorer:password@db:5432/explorer_db
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
      - model_cache:/root/.cache  # ⭐ 新增：模型缓存卷
    depends_on:
      - db
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: pgvector/pgvector:pg16
    container_name: explorer_db
    environment:
      POSTGRES_USER: explorer
      POSTGRES_PASSWORD: password
      POSTGRES_DB: explorer_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    container_name: explorer_redis
    ports:
      - "6379:6379"

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: explorer_celery
    environment:
      - DATABASE_URL=postgresql://explorer:password@db:5432/explorer_db
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
      - model_cache:/root/.cache  # ⭐ 新增：模型缓存卷
    depends_on:
      - db
      - redis
    command: celery -A app.tasks.worker worker --loglevel=info

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: explorer_frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend

volumes:
  postgres_data:
  model_cache:  # ⭐ 新增：持久化模型缓存
```

### 4. 更新backend Dockerfile

`backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements-v2.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements-v2.txt

# 下载spaCy模型
RUN python -m spacy download zh_core_web_sm

# 预下载sentence-transformers模型 (可选，加速首次启动)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Week 1-2: Organizer Agent实施

### 步骤1: 创建数据库表

创建 `backend/alembic/versions/003_add_organizer_tables.py`:

```python
"""add organizer tables

Revision ID: 003
Revises: 002_add_thinker_tables
Create Date: 2025-12-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002_add_thinker_tables'
branch_labels = None
depends_on = None


def upgrade():
    # 知识图谱节点表
    op.create_table(
        'knowledge_nodes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('node_type', sa.String(50), nullable=False),  # paper, concept, author, insight, method, dataset
        sa.Column('title', sa.String(500)),
        sa.Column('description', sa.Text()),
        sa.Column('metadata', postgresql.JSONB()),
        sa.Column('source_node_id', sa.Integer()),  # 来自nodes表还是insights表
        sa.Column('source_type', sa.String(50)),  # 'node' or 'insight'
        sa.Column('embedding', postgresql.ARRAY(sa.Float())),  # 向量嵌入
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now())
    )

    # 知识图谱边表
    op.create_table(
        'knowledge_edges',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('source_id', sa.Integer(), nullable=False),  # knowledge_nodes.id
        sa.Column('target_id', sa.Integer(), nullable=False),  # knowledge_nodes.id
        sa.Column('edge_type', sa.String(50), nullable=False),  # cites, discusses, uses, applies_to, etc.
        sa.Column('weight', sa.Float(), default=1.0),
        sa.Column('metadata', postgresql.JSONB()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    # 主题聚类表
    op.create_table(
        'topic_clusters',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('cluster_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('item_ids', postgresql.ARRAY(sa.Integer())),  # 包含的节点/洞察ID
        sa.Column('cluster_center', postgresql.ARRAY(sa.Float())),  # 聚类中心向量
        sa.Column('item_count', sa.Integer(), default=0),
        sa.Column('confidence', sa.Float()),  # 聚类置信度
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    # 时间线事件表
    op.create_table(
        'timeline_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('event_type', sa.String(50)),  # breakthrough, publication, trend_change
        sa.Column('title', sa.String(500)),
        sa.Column('description', sa.Text()),
        sa.Column('related_node_ids', postgresql.ARRAY(sa.Integer())),
        sa.Column('impact_level', sa.String(20)),  # high, medium, low
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    # 趋势指标表
    op.create_table(
        'trend_metrics',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('metric_date', sa.Date(), nullable=False),
        sa.Column('keyword', sa.String(100), nullable=False),
        sa.Column('frequency', sa.Integer(), default=0),
        sa.Column('trend_direction', sa.String(20)),  # rising, stable, declining
        sa.Column('score', sa.Float()),  # 趋势分数
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    # 研究问题表
    op.create_table(
        'research_questions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(50)),  # gap, contradiction, opportunity
        sa.Column('context', postgresql.JSONB()),
        sa.Column('importance', sa.String(20)),  # high, medium, low
        sa.Column('suggested_exploration', sa.String(500)),
        sa.Column('status', sa.String(20), default='open'),  # open, answered
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    # 创建索引
    op.create_index('ix_knowledge_nodes_type', 'knowledge_nodes', ['node_type'])
    op.create_index('ix_knowledge_edges_source_target', 'knowledge_edges', ['source_id', 'target_id'])
    op.create_index('ix_topic_clusters_name', 'topic_clusters', ['cluster_name'])
    op.create_index('ix_timeline_events_date', 'timeline_events', ['event_date'])
    op.create_index('ix_trend_metrics_keyword_date', 'trend_metrics', ['keyword', 'metric_date'])


def downgrade():
    op.drop_table('research_questions')
    op.drop_table('trend_metrics')
    op.drop_table('timeline_events')
    op.drop_table('topic_clusters')
    op.drop_table('knowledge_edges')
    op.drop_table('knowledge_nodes')
```

运行迁移:

```bash
docker-compose exec backend alembic upgrade head
```

### 步骤2: 创建Organizer Agent基础结构

`backend/app/agents/organizer.py`:

```python
from typing import Dict, List, Any, Optional
from app.agents.base import AgentProtocol
from app.db.database import get_db
from app.models.knowledge import (
    KnowledgeNode, KnowledgeEdge,
    TopicCluster, TimelineEvent, TrendMetric, ResearchQuestion
)
from app.services.organizer.graph_builder import KnowledgeGraphBuilder
from app.services.organizer.topic_clusterer import TopicClusterer
from app.services.organizer.timeline_analyzer import TimelineAnalyzer
from app.services.organizer.question_discoverer import QuestionDiscoverer
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class OrganizerAgent(AgentProtocol):
    """
    整理者 - 知识架构师

    职责:
    1. 构建知识图谱
    2. 主题聚类
    3. 时间线分析
    4. 趋势识别
    5. 问题发现
    """

    def __init__(self,
                 graph_builder: Optional[KnowledgeGraphBuilder] = None,
                 topic_clusterer: Optional[TopicClusterer] = None,
                 timeline_analyzer: Optional[TimelineAnalyzer] = None,
                 question_discoverer: Optional[QuestionDiscoverer] = None):
        """
        初始化Organizer Agent

        Args:
            graph_builder: 知识图谱构建器
            topic_clusterer: 主题聚类器
            timeline_analyzer: 时间线分析器
            question_discoverer: 问题发现器
        """
        self.graph_builder = graph_builder or KnowledgeGraphBuilder()
        self.topic_clusterer = topic_clusterer or TopicClusterer()
        self.timeline_analyzer = timeline_analyzer or TimelineAnalyzer()
        self.question_discoverer = question_discoverer or QuestionDiscoverer()

    def validate_input(self, input_data: Dict) -> bool:
        """验证输入数据"""
        required_keys = ['high_quality', 'insights']

        for key in required_keys:
            if key not in input_data:
                logger.error(f"Missing required key: {key}")
                return False

        return True

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行整理流程

        Args:
            input_data: {
                "high_quality": List[Node],  # 高质量节点
                "insights": List[Insight]    # 洞察列表
            }

        Returns:
            {
                "status": "success" | "partial" | "failed",
                "data": {
                    "knowledge_graph": {...},
                    "topics": {...},
                    "timeline": [...],
                    "trends": {...},
                    "questions": [...]
                },
                "metrics": {...},
                "errors": [...]
            }
        """
        import time
        start_time = time.time()

        errors = []

        # 验证输入
        if not self.validate_input(input_data):
            return {
                "status": "failed",
                "data": None,
                "metrics": {},
                "errors": ["Input validation failed"]
            }

        high_quality = input_data.get("high_quality", [])
        insights = input_data.get("insights", [])

        try:
            # 1. 构建知识图谱
            logger.info("Building knowledge graph...")
            graph_result = self.graph_builder.build(high_quality, insights)
            graph_metrics = graph_result.get("metrics", {})

            # 2. 主题聚类
            logger.info("Clustering topics...")
            all_items = high_quality + insights
            topics_result = self.topic_clusterer.cluster(all_items)

            # 3. 时间线分析
            logger.info("Analyzing timeline...")
            timeline_result = self.timeline_analyzer.analyze(all_items)

            # 4. 趋势识别
            logger.info("Identifying trends...")
            trends_result = self.timeline_analyzer.identify_trends(all_items)

            # 5. 问题发现
            logger.info("Discovering questions...")
            questions_result = self.question_discoverer.discover(
                graph_result.get("graph"),
                topics_result.get("clusters")
            )

            execution_time = time.time() - start_time

            return {
                "status": "success",
                "data": {
                    "knowledge_graph": graph_result,
                    "topics": topics_result,
                    "timeline": timeline_result,
                    "trends": trends_result,
                    "questions": questions_result
                },
                "metrics": {
                    "nodes_processed": len(all_items),
                    "graph_nodes": graph_metrics.get("nodes_count", 0),
                    "graph_edges": graph_metrics.get("edges_count", 0),
                    "topics_found": len(topics_result.get("clusters", [])),
                    "timeline_events": len(timeline_result.get("events", [])),
                    "trends_identified": len(trends_result.get("rising", [])),
                    "questions_found": len(questions_result.get("questions", [])),
                    "execution_time": execution_time
                },
                "errors": errors
            }

        except Exception as e:
            logger.error(f"Organizer agent failed: {str(e)}", exc_info=True)
            errors.append(str(e))

            return {
                "status": "failed",
                "data": None,
                "metrics": {"execution_time": time.time() - start_time},
                "errors": errors
            }

    def get_config(self) -> Dict:
        """获取配置"""
        return {
            "agent_type": "OrganizerAgent",
            "components": {
                "graph_builder": self.graph_builder.__class__.__name__,
                "topic_clusterer": self.topic_clusterer.__class__.__name__,
                "timeline_analyzer": self.timeline_analyzer.__class__.__name__,
                "question_discoverer": self.question_discoverer.__class__.__name__
            }
        }
```

### 步骤3: 实现KnowledgeGraphBuilder

创建 `backend/app/services/organizer/graph_builder.py`:

```python
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.knowledge import KnowledgeNode, KnowledgeEdge
import networkx as nx
import logging

logger = logging.getLogger(__name__)


class KnowledgeGraphBuilder:
    """
    知识图谱构建器

    功能:
    1. 从节点和洞察创建知识图谱节点
    2. 识别节点间关系，创建边
    3. 使用NetworkX进行图分析
    """

    def __init__(self):
        self.graph = nx.DiGraph()

    def build(self,
              high_quality_nodes: List[Any],
              insights: List[Any]) -> Dict[str, Any]:
        """
        构建知识图谱

        Args:
            high_quality_nodes: 高质量节点列表
            insights: 洞察列表

        Returns:
            {
                "graph": nx.Graph,
                "nodes": List[KnowledgeNode],
                "edges": List[KnowledgeEdge],
                "metrics": {...}
            }
        """
        db = next(get_db())

        try:
            # 1. 创建节点
            knowledge_nodes = self._create_nodes(db, high_quality_nodes, insights)

            # 2. 创建边
            knowledge_edges = self._create_edges(db, knowledge_nodes)

            # 3. 构建NetworkX图
            graph = self._build_networkx_graph(knowledge_nodes, knowledge_edges)

            # 4. 计算图指标
            metrics = self._compute_graph_metrics(graph)

            return {
                "graph": graph,
                "nodes": knowledge_nodes,
                "edges": knowledge_edges,
                "metrics": metrics
            }

        finally:
            db.close()

    def _create_nodes(self,
                     db: Session,
                     high_quality_nodes: List[Any],
                     insights: List[Any]) -> List[KnowledgeNode]:
        """创建知识图谱节点"""
        knowledge_nodes = []

        # 从高质量节点创建
        for node in high_quality_nodes:
            kn = KnowledgeNode(
                node_type="paper",
                title=node.title,
                description=node.content[:500] if node.content else None,
                metadata={
                    "source": node.source,
                    "url": node.url,
                    "value_score": node.value_score,
                    "tags": node.tags
                },
                source_node_id=node.id,
                source_type="node"
            )
            db.add(kn)
            knowledge_nodes.append(kn)

        # 从洞察创建
        for insight in insights:
            kn = KnowledgeNode(
                node_type="insight",
                title=insight.title,
                description=insight.content,
                metadata={
                    "insight_type": insight.insight_type,
                    "related_nodes": insight.related_node_ids,
                    "confidence": insight.confidence
                },
                source_node_id=insight.id,
                source_type="insight"
            )
            db.add(kn)
            knowledge_nodes.append(kn)

        db.commit()

        logger.info(f"Created {len(knowledge_nodes)} knowledge nodes")
        return knowledge_nodes

    def _create_edges(self,
                     db: Session,
                     knowledge_nodes: List[KnowledgeNode]) -> List[KnowledgeEdge]:
        """创建知识图谱边"""
        edges = []

        # 简单策略: 基于标签相似性创建边
        for i, node1 in enumerate(knowledge_nodes):
            for node2 in knowledge_nodes[i+1:]:
                similarity = self._compute_similarity(node1, node2)

                if similarity > 0.5:  # 相似度阈值
                    edge = KnowledgeEdge(
                        source_id=node1.id,
                        target_id=node2.id,
                        edge_type="related_to",
                        weight=similarity,
                        metadata={"similarity": similarity}
                    )
                    db.add(edge)
                    edges.append(edge)

        db.commit()

        logger.info(f"Created {len(edges)} knowledge edges")
        return edges

    def _compute_similarity(self,
                          node1: KnowledgeNode,
                          node2: KnowledgeNode) -> float:
        """计算节点相似度"""
        # 简单实现: 基于标签重叠
        tags1 = set(node1.metadata.get("tags", []))
        tags2 = set(node2.metadata.get("tags", []))

        if not tags1 or not tags2:
            return 0.0

        intersection = len(tags1 & tags2)
        union = len(tags1 | tags2)

        return intersection / union if union > 0 else 0.0

    def _build_networkx_graph(self,
                             nodes: List[KnowledgeNode],
                             edges: List[KnowledgeEdge]) -> nx.DiGraph:
        """构建NetworkX图"""
        graph = nx.DiGraph()

        # 添加节点
        for node in nodes:
            graph.add_node(
                node.id,
                node_type=node.node_type,
                title=node.title,
                description=node.description
            )

        # 添加边
        for edge in edges:
            graph.add_edge(
                edge.source_id,
                edge.target_id,
                edge_type=edge.edge_type,
                weight=edge.weight
            )

        return graph

    def _compute_graph_metrics(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """计算图指标"""
        return {
            "nodes_count": graph.number_of_nodes(),
            "edges_count": graph.number_of_edges(),
            "density": nx.density(graph),
            "is_connected": nx.is_weakly_connected(graph)
        }
```

### 步骤4: 实现TopicClusterer

创建 `backend/app/services/organizer/topic_clusterer.py`:

```python
from typing import Dict, List, Any
from sentence_transformers import SentenceTransformer
import umap
import hdbscan
from app.db.database import get_db
from app.models.knowledge import TopicCluster
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class TopicClusterer:
    """
    主题聚类器

    流程:
    1. 生成文本嵌入 (sentence-transformers)
    2. 降维 (UMAP)
    3. 聚类 (HDBSCAN)
    4. 命名主题
    """

    def __init__(self):
        # 加载嵌入模型
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        # UMAP配置
        self.umap_model = umap.UMAP(
            n_neighbors=15,
            n_components=5,
            metric='cosine'
        )

        # HDBSCAN配置
        self.cluster_model = hdbscan.HDBSCAN(
            min_cluster_size=3,
            metric='euclidean',
            cluster_selection_method='eom'
        )

    def cluster(self, items: List[Any]) -> Dict[str, Any]:
        """
        聚类主题

        Args:
            items: 节点和洞察列表

        Returns:
            {
                "clusters": List[Dict],
                "metrics": {...}
            }
        """
        if len(items) < 3:
            logger.warning("Not enough items to cluster")
            return {
                "clusters": [],
                "metrics": {"clusters_found": 0}
            }

        db = next(get_db())

        try:
            # 1. 准备文本
            texts = [item.title + " " + (item.content[:500] if hasattr(item, 'content') and item.content else "")
                    for item in items]

            # 2. 生成嵌入
            embeddings = self.model.encode(texts, show_progress_bar=False)

            # 3. 降维
            reduced_embeddings = self.umap_model.fit_transform(embeddings)

            # 4. 聚类
            clusters = self.cluster_model.fit_predict(reduced_embeddings)

            # 5. 创建主题聚类记录
            topic_clusters = self._create_clusters(
                db,
                items,
                clusters,
                reduced_embeddings
            )

            return {
                "clusters": [
                    {
                        "id": tc.id,
                        "name": tc.cluster_name,
                        "description": tc.description,
                        "item_count": tc.item_count,
                        "confidence": tc.confidence
                    }
                    for tc in topic_clusters
                ],
                "metrics": {
                    "clusters_found": len(topic_clusters),
                    "noise_points": sum(1 for c in clusters if c == -1)
                }
            }

        finally:
            db.close()

    def _create_clusters(self,
                        db: Session,
                        items: List[Any],
                        cluster_labels: List[int],
                        embeddings: List[List[float]]) -> List[TopicCluster]:
        """创建主题聚类记录"""
        unique_clusters = set(cluster_labels) - {-1}  # 排除噪声
        topic_clusters = []

        for cluster_id in unique_clusters:
            # 获取该聚类的所有item
            cluster_items = [
                item for item, label in zip(items, cluster_labels)
                if label == cluster_id
            ]

            # 生成聚类名称
            cluster_name = self._generate_cluster_name(cluster_items)

            # 计算聚类中心
            cluster_embeddings = [
                emb for emb, label in zip(embeddings, cluster_labels)
                if label == cluster_id
            ]
            cluster_center = sum(cluster_embeddings) / len(cluster_embeddings)

            # 创建数据库记录
            tc = TopicCluster(
                cluster_name=cluster_name,
                description=f"Cluster with {len(cluster_items)} items",
                item_ids=[item.id for item in cluster_items],
                cluster_center=cluster_center.tolist(),
                item_count=len(cluster_items),
                confidence=self._compute_confidence(cluster_labels, cluster_id)
            )
            db.add(tc)
            topic_clusters.append(tc)

        db.commit()
        return topic_clusters

    def _generate_cluster_name(self, items: List[Any]) -> str:
        """生成聚类名称"""
        # 简单实现: 使用最常见的标签
        all_tags = []
        for item in items:
            if hasattr(item, 'tags') and item.tags:
                all_tags.extend(item.tags)

        if all_tags:
            from collections import Counter
            most_common = Counter(all_tags).most_common(3)
            return ", ".join([tag for tag, _ in most_common])

        return f"Cluster {len(items)} items"

    def _compute_confidence(self,
                           cluster_labels: List[int],
                           cluster_id: int) -> float:
        """计算聚类置信度"""
        cluster_size = sum(1 for label in cluster_labels if label == cluster_id)
        total_size = len(cluster_labels)

        # 简单的置信度计算
        return cluster_size / total_size
```

### 步骤5: 测试Organizer Agent

创建 `backend/tests/test_organizer.py`:

```python
import pytest
from app.agents.organizer import OrganizerAgent
from app.db.database import get_db
from app.models.node import Node
from app.models.insight import Insight


def test_organizer_agent_basic():
    """测试Organizer Agent基本功能"""
    organizer = OrganizerAgent()

    # 准备测试数据
    db = next(get_db())

    # 创建测试节点
    test_nodes = [
        Node(
            title="Test Paper 1",
            content="This is about machine learning",
            source="arxiv",
            value_score=0.8,
            tags=["AI", "ML"]
        ),
        Node(
            title="Test Paper 2",
            content="This is about deep learning",
            source="arxiv",
            value_score=0.7,
            tags=["AI", "DL"]
        )
    ]

    for node in test_nodes:
        db.add(node)
    db.commit()

    # 创建测试洞察
    test_insights = [
        Insight(
            title="Test Insight",
            content="Machine learning and deep learning are related",
            insight_type="connection",
            related_node_ids=[test_nodes[0].id, test_nodes[1].id],
            confidence=0.8
        )
    ]

    for insight in test_insights:
        db.add(insight)
    db.commit()

    # 运行Organizer
    input_data = {
        "high_quality": test_nodes,
        "insights": test_insights
    }

    result = organizer.run(input_data)

    # 验证结果
    assert result["status"] == "success"
    assert "knowledge_graph" in result["data"]
    assert "topics" in result["data"]
    assert result["metrics"]["nodes_processed"] == 3

    # 清理
    for node in test_nodes:
        db.delete(node)
    for insight in test_insights:
        db.delete(insight)
    db.commit()


if __name__ == "__main__":
    test_organizer_agent_basic()
    print("Organizer Agent test passed!")
```

运行测试:

```bash
docker-compose exec backend python tests/test_organizer.py
```

---

## Week 3-4: Outputter Agent实施

### 步骤1: 创建Outputter数据库表

创建 `backend/alembic/versions/004_add_outputter_tables.py`:

```python
"""add outputter tables

Revision ID: 004
Revises: 003_add_organizer_tables
Create Date: 2025-12-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003_add_organizer_tables'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'generated_reports',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('report_type', sa.String(50), nullable=False),  # daily, weekly, insight_brief
        sa.Column('title', sa.String(500)),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('format', sa.String(20), default='markdown'),  # markdown, html, json
        sa.Column('metadata', postgresql.JSONB()),
        sa.Column('file_path', sa.String(500)),  # 生成的文件路径
        sa.Column('feedback_to_explorer', postgresql.JSONB()),  # 反馈给探索者的建议
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    op.create_index('ix_generated_reports_type', 'generated_reports', ['report_type'])


def downgrade():
    op.drop_table('generated_reports')
```

运行迁移:

```bash
docker-compose exec backend alembic upgrade head
```

### 步骤2: 创建Outputter Agent

创建 `backend/app/agents/outputter.py`:

```python
from typing import Dict, List, Any, Optional
from app.agents.base import AgentProtocol
from app.services.outputter.report_generator import ReportGenerator
from app.services.outputter.visualization_generator import VisualizationGenerator
from app.services.outputter.feedback_generator import FeedbackGenerator
from app.db.database import get_db
from app.models.outputter import GeneratedReport
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class OutputterAgent(AgentProtocol):
    """
    输出者 - 报告生成器

    职责:
    1. 生成日报、周报
    2. 生成洞察简报
    3. 生成可视化数据
    4. 生成反馈给Explorer
    """

    def __init__(self,
                 report_generator: Optional[ReportGenerator] = None,
                 visualization_generator: Optional[VisualizationGenerator] = None,
                 feedback_generator: Optional[FeedbackGenerator] = None,
                 output_dir: str = "outputs"):
        self.report_generator = report_generator or ReportGenerator()
        self.visualization_generator = visualization_generator or VisualizationGenerator()
        self.feedback_generator = feedback_generator or FeedbackGenerator()
        self.output_dir = output_dir

    def validate_input(self, input_data: Dict) -> bool:
        """验证输入数据"""
        required_keys = ['knowledge_graph', 'topics', 'timeline', 'trends', 'questions']

        for key in required_keys:
            if key not in input_data:
                logger.error(f"Missing required key: {key}")
                return False

        return True

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行输出流程

        Args:
            input_data: Organizer的输出

        Returns:
            {
                "status": "success" | "partial" | "failed",
                "data": {
                    "daily_report": str,
                    "weekly_digest": str,
                    "insight_briefs": List[str],
                    "visualizations": Dict,
                    "feedback_to_explorer": List[str]
                },
                "metrics": {...},
                "errors": [...]
            }
        """
        import time
        start_time = time.time()
        errors = []

        if not self.validate_input(input_data):
            return {
                "status": "failed",
                "data": None,
                "metrics": {},
                "errors": ["Input validation failed"]
            }

        try:
            # 1. 生成日报
            logger.info("Generating daily report...")
            daily_report = self.report_generator.generate_daily_report(input_data)

            # 2. 生成周报
            logger.info("Generating weekly digest...")
            weekly_digest = self.report_generator.generate_weekly_digest(input_data)

            # 3. 生成洞察简报
            logger.info("Generating insight briefs...")
            insight_briefs = self.report_generator.generate_insight_briefs(input_data)

            # 4. 生成可视化
            logger.info("Generating visualizations...")
            visualizations = self.visualization_generator.generate_all(input_data, self.output_dir)

            # 5. 生成反馈
            logger.info("Generating feedback...")
            feedback = self.feedback_generator.generate_feedback(input_data)

            execution_time = time.time() - start_time

            # 保存到数据库
            self._save_reports({
                "daily_report": daily_report,
                "weekly_digest": weekly_digest,
                "insight_briefs": insight_briefs,
                "visualizations": visualizations,
                "feedback": feedback
            })

            return {
                "status": "success",
                "data": {
                    "daily_report": daily_report,
                    "weekly_digest": weekly_digest,
                    "insight_briefs": insight_briefs,
                    "visualizations": visualizations,
                    "feedback_to_explorer": feedback
                },
                "metrics": {
                    "reports_generated": 3,
                    "visualizations_created": len(visualizations),
                    "feedback_items": len(feedback),
                    "execution_time": execution_time
                },
                "errors": errors
            }

        except Exception as e:
            logger.error(f"Outputter agent failed: {str(e)}", exc_info=True)
            errors.append(str(e))

            return {
                "status": "failed",
                "data": None,
                "metrics": {"execution_time": time.time() - start_time},
                "errors": errors
            }

    def _save_reports(self, reports: Dict[str, Any]):
        """保存报告到数据库"""
        db = next(get_db())

        try:
            # 保存日报
            daily_report = GeneratedReport(
                report_type="daily",
                title="Daily Exploration Report",
                content=reports["daily_report"],
                format="markdown",
                feedback_to_explorer={"suggestions": reports["feedback"]}
            )
            db.add(daily_report)

            # 保存周报
            weekly_report = GeneratedReport(
                report_type="weekly",
                title="Weekly Digest",
                content=reports["weekly_digest"],
                format="markdown",
                feedback_to_explorer={"suggestions": reports["feedback"]}
            )
            db.add(weekly_report)

            db.commit()
            logger.info("Reports saved to database")

        finally:
            db.close()
```

### 步骤3: 实现ReportGenerator

创建 `backend/app/services/outputter/report_generator.py`:

```python
from typing import Dict, List, Any
from datetime import datetime
from jinja2 import Template
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器"""

    def generate_daily_report(self, data: Dict[str, Any]) -> str:
        """生成日报"""
        template_str = """# 知识探索日报 - {{ date }}

## 📈 今日数据
- 新发现: {{ new_items }} 篇
- 高质量: {{ high_quality }} 篇
- 洞察: {{ insights }} 条
- 新关联: {{ connections }} 对

## 🔥 今日亮点
{% for highlight in highlights %}
### {{ highlight.title }}
{{ highlight.description }}
**影响**: {{ highlight.impact }}
**建议**: {{ highlight.suggestion }}
{% endfor %}

## 📊 趋势
{% for trend in trends %}
- {{ trend.direction }} {{ trend.keyword }}

{% endfor %}
## 💡 明日建议
{% for suggestion in suggestions %}
{{ loop.index }}. {{ suggestion }}
{% endfor %}
"""

        template = Template(template_str)

        # 准备数据
        metrics = data.get("knowledge_graph", {}).get("metrics", {})
        topics = data.get("topics", {}).get("clusters", [])
        trends = data.get("trends", {})
        questions = data.get("questions", {}).get("questions", [])

        return template.render(
            date=datetime.now().strftime("%Y-%m-%d"),
            new_items=metrics.get("nodes_processed", 0),
            high_quality=metrics.get("nodes_count", 0),
            insights=0,  # 从data中提取
            connections=metrics.get("edges_count", 0),
            highlights=self._extract_highlights(data),
            trends=[
                {"direction": "🔼", "keyword": k}
                for k in trends.get("rising", [])[:5]
            ],
            suggestions=[
                q.get("suggested_exploration", "")
                for q in questions[:3]
            ]
        )

    def generate_weekly_digest(self, data: Dict[str, Any]) -> str:
        """生成周报"""
        # 简化实现，实际应该聚合一周的数据
        return f"""# 本周知识总结 - Week {datetime.now().isocalendar()[1]}

本周探索发现多个主题聚类。

详细内容请查看日报。
"""

    def generate_insight_briefs(self, data: Dict[str, Any]) -> List[str]:
        """生成洞察简报"""
        questions = data.get("questions", {}).get("questions", [])
        briefs = []

        for i, question in enumerate(questions[:5], 1):
            brief = f"""# 洞察简报 #{i}

## 问题
{question.get('question', 'N/A')}

## 重要性
{question.get('importance', 'N/A')}

## 建议探索
{question.get('suggested_exploration', 'N/A')}
"""
            briefs.append(brief)

        return briefs

    def _extract_highlights(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """提取亮点"""
        highlights = []

        # 从高质量节点中提取
        graph_data = data.get("knowledge_graph", {})
        nodes = graph_data.get("nodes", [])

        for node in nodes[:3]:
            if node.node_type == "paper":
                highlights.append({
                    "title": node.title,
                    "description": node.description[:200] if node.description else "",
                    "impact": "可能改变baseline" if node.metadata.get("value_score", 0) > 0.8 else "有参考价值",
                    "suggestion": "关注其代码开源情况"
                })

        return highlights
```

### 步骤4: 测试Outputter Agent

创建 `backend/tests/test_outputter.py`:

```python
from app.agents.outputter import OutputterAgent


def test_outputter_agent_basic():
    """测试Outputter Agent基本功能"""
    outputter = OutputterAgent()

    # 准备测试数据
    input_data = {
        "knowledge_graph": {
            "metrics": {
                "nodes_count": 10,
                "edges_count": 15
            }
        },
        "topics": {
            "clusters": []
        },
        "timeline": {
            "events": []
        },
        "trends": {
            "rising": ["AI", "ML"]
        },
        "questions": {
            "questions": [
                {
                    "question": "Test question",
                    "importance": "high",
                    "suggested_exploration": "test exploration"
                }
            ]
        }
    }

    result = outputter.run(input_data)

    # 验证
    assert result["status"] == "success"
    assert "daily_report" in result["data"]
    assert "feedback_to_explorer" in result["data"]
    assert result["metrics"]["reports_generated"] == 3

    print("Daily Report:")
    print(result["data"]["daily_report"])

    print("\nFeedback to Explorer:")
    for feedback in result["data"]["feedback_to_explorer"]:
        print(f"- {feedback}")


if __name__ == "__main__":
    test_outputter_agent_basic()
    print("\nOutputter Agent test passed!")
```

---

## Week 5: 闭环与编排

### 创建Orchestrator Agent

创建 `backend/app/agents/orchestrator.py`:

```python
from typing import Dict, Any, List
from app.agents.base import AgentProtocol
from app.agents.explorer import ExplorerAgent
from app.agents.evaluator import EvaluatorAgent
from app.agents.thinker import ThinkerAgent
from app.agents.organizer import OrganizerAgent
from app.agents.outputter import OutputterAgent
import logging

logger = logging.getLogger(__name__)


class OrchestratorAgent(AgentProtocol):
    """
    编排者 - 协调所有AGENT

    职责:
    1. 按顺序执行所有AGENT
    2. 传递数据
    3. 处理错误
    4. 反馈优化
    """

    def __init__(self,
                 explorer: ExplorerAgent,
                 evaluator: EvaluatorAgent,
                 thinker: ThinkerAgent,
                 organizer: OrganizerAgent,
                 outputter: OutputterAgent):
        self.explorer = explorer
        self.evaluator = evaluator
        self.thinker = thinker
        self.organizer = organizer
        self.outputter = outputter

    def validate_input(self, input_data: Dict) -> bool:
        """验证输入"""
        return "query" in input_data or "seeds" in input_data

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行完整闭环流程

        流程:
        Explorer → Evaluator → Thinker → Organizer → Outputter → 反馈到 Explorer
        """
        import time
        start_time = time.time()
        errors = []

        # 1. 探索
        logger.info("=== Step 1: Exploration ===")
        exploration_result = self.explorer.run(input_data)

        if exploration_result["status"] == "failed":
            return {
                "status": "failed",
                "stage": "exploration",
                "errors": exploration_result["errors"]
            }

        all_items = exploration_result["data"]["discovered"]
        high_quality = exploration_result["data"].get("high_quality", [])
        low_quality = exploration_result["data"].get("low_quality", [])

        logger.info(f"Discovered {len(all_items)} items ({len(high_quality)} high quality, {len(low_quality)} low quality)")

        # 2. 思考 (如果有低质量内容)
        insights = []
        if low_quality:
            logger.info("=== Step 2: Thinking ===")
            thinking_result = self.thinker.run({"items": low_quality})

            if thinking_result["status"] == "success":
                insights = thinking_result["data"].get("insights", [])
                logger.info(f"Generated {len(insights)} insights")
            else:
                errors.extend(thinking_result.get("errors", []))

        # 3. 整理
        logger.info("=== Step 3: Organization ===")
        organization_result = self.organizer.run({
            "high_quality": high_quality,
            "insights": insights
        })

        if organization_result["status"] == "failed":
            return {
                "status": "failed",
                "stage": "organization",
                "errors": organization_result["errors"]
            }

        # 4. 输出
        logger.info("=== Step 4: Output ===")
        output_result = self.outputter.run(organization_result["data"])

        if output_result["status"] == "failed":
            errors.extend(output_result.get("errors", []))

        # 5. 反馈
        feedback = output_result["data"].get("feedback_to_explorer", [])
        logger.info(f"=== Step 5: Feedback ({len(feedback)} suggestions) ===")

        execution_time = time.time() - start_time

        return {
            "status": "success" if not errors or output_result["status"] == "success" else "partial",
            "data": {
                "exploration": exploration_result["data"],
                "thinking": {"insights_count": len(insights)},
                "organization": organization_result["data"],
                "output": output_result["data"]
            },
            "feedback": feedback,
            "metrics": {
                "total_items": len(all_items),
                "high_quality_count": len(high_quality),
                "insights_count": len(insights),
                "execution_time": execution_time
            },
            "errors": errors
        }


def create_orchestrator(config: Dict[str, Any]) -> OrchestratorAgent:
    """创建Orchestrator实例"""
    # 这里需要根据config创建各个AGENT实例
    # 简化示例

    from app.services.sources.arxiv import ArxivSource
    from app.services.sources.web import WebSource

    explorer = ExplorerAgent(
        sources=[ArxivSource(), WebSource()],
        evaluator=EvaluatorAgent(),
        storage=None  # 使用默认
    )

    thinker = ThinkerAgent()
    organizer = OrganizerAgent()
    outputter = OutputterAgent()

    return OrchestratorAgent(
        explorer=explorer,
        evaluator=EvaluatorAgent(),  # explorer已有evaluator，这里简化
        thinker=thinker,
        organizer=organizer,
        outputter=outputter
    )
```

### 测试完整闭环

创建 `backend/tests/test_full_cycle.py`:

```python
from app.agents.orchestrator import create_orchestrator


def test_full_cycle():
    """测试完整闭环流程"""
    orchestrator = create_orchestrator({})

    # 运行完整流程
    result = orchestrator.run({
        "query": "machine learning",
        "max_results": 5
    })

    print("=== Full Cycle Result ===")
    print(f"Status: {result['status']}")
    print(f"Total Items: {result['metrics']['total_items']}")
    print(f"High Quality: {result['metrics']['high_quality_count']}")
    print(f"Insights: {result['metrics']['insights_count']}")
    print(f"Execution Time: {result['metrics']['execution_time']:.2f}s")

    print("\n=== Feedback to Explorer ===")
    for i, feedback in enumerate(result['feedback'], 1):
        print(f"{i}. {feedback}")

    # 保存日报
    if result["status"] == "success":
        daily_report = result["data"]["output"]["daily_report"]
        with open("outputs/daily_report.md", "w", encoding="utf-8") as f:
            f.write(daily_report)
        print("\nDaily report saved to outputs/daily_report.md")


if __name__ == "__main__":
    test_full_cycle()
```

---

## 部署指南

### 1. 本地部署

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 运行完整流程
docker-compose exec backend python tests/test_full_cycle.py
```

### 2. 定时任务配置

创建 `backend/scripts/automated_v2.py`:

```python
"""
自动化探索 v2.0 - 完整闭环
"""
import schedule
import time
from app.agents.orchestrator import create_orchestrator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_daily_exploration():
    """每日自动探索"""
    logger.info("Starting daily exploration...")

    orchestrator = create_orchestrator({})
    result = orchestrator.run({
        "query": "machine learning",  # 可以从配置读取
        "max_results": 20
    })

    if result["status"] == "success":
        logger.info(f"Daily exploration completed: {result['metrics']}")

        # 发送邮件通知 (可选)
        # send_email_report(result["data"]["output"]["daily_report"])
    else:
        logger.error(f"Daily exploration failed: {result['errors']}")


def main():
    # 每天早上8点运行
    schedule.every().day.at("08:00").do(run_daily_exploration)

    logger.info("Scheduler started. Waiting for next run...")

    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次


if __name__ == "__main__":
    main()
```

更新docker-compose.yml添加celery beat:

```yaml
  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: explorer_celery_beat
    environment:
      - DATABASE_URL=postgresql://explorer:password@db:5432/explorer_db
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
      - model_cache:/root/.cache
    depends_on:
      - db
      - redis
    command: celery -A app.tasks.worker beat --loglevel=info
```

---

## 常见问题

### Q1: 模型加载慢怎么办？

**A**: 预下载模型并挂载到Docker卷

```bash
# 在本地下载模型
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# 模型会缓存在 ~/.cache/torch/sentence_transformers/
# docker-compose.yml 已添加 model_cache 卷
```

### Q2: 内存不足怎么办？

**A**: 调整UMAP和HDBSCAN参数，减少内存使用

```python
# 在topic_clusterer.py中
self.umap_model = umap.UMAP(
    n_neighbors=10,  # 减少从15
    n_components=3,  # 减少从5
    metric='cosine'
)

self.cluster_model = hdbscan.HDBSCAN(
    min_cluster_size=5,  # 增加从3，减少聚类数
    memory=None  # 不使用memory缓存
)
```

### Q3: 如何监控运行状态？

**A**: 添加健康检查端点

```python
# backend/app/api/v1/endpoints/health.py
@router.get("/health/v2")
async def health_check_v2():
    return {
        "status": "healthy",
        "agents": {
            "explorer": "ready",
            "evaluator": "ready",
            "thinker": "ready",
            "organizer": "ready",
            "outputter": "ready"
        },
        "last_cycle": get_last_cycle_time()
    }
```

### Q4: 如何优化性能？

**A**:
1. 使用批处理评估
2. 缓存嵌入向量
3. 异步处理非关键步骤
4. 使用数据库索引

---

## 下一步

完成实施后，您将拥有:

✅ 5-Agent完整闭环系统
✅ 自动化知识发现和整理
✅ 结构化输出（日报、周报、洞察简报）
✅ 可视化知识图谱和主题聚类
✅ 反馈优化机制

系统将完全自动化，无需人工干预即可持续运行，为用户提供有价值的知识洞察。
