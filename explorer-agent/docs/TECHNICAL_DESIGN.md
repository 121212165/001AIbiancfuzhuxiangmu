# Explorer Agent v2.0 - 技术设计与选型

**版本**: 2.0
**创建日期**: 2025-12-29
**文档类型**: 技术设计规范

---

## 目录

1. [系统架构概览](#1-系统架构概览)
2. [Organizer Agent详细设计](#2-organizer-agent详细设计)
3. [Outputter Agent详细设计](#3-outputter-agent详细设计)
4. [技术栈选型](#4-技术栈选型)
5. [数据模型设计](#5-数据模型设计)
6. [API接口设计](#6-api接口设计)
7. [实施指南](#7-实施指南)

---

## 1. 系统架构概览

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    应用层                                  │
├─────────────────────────────────────────────────────────────┤
│  CLI / Scheduler / Web Interface (可选)                   │
└──────────────────────┬────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                 Orchestrator (编排层)                       │
├─────────────────────────────────────────────────────────────┤
│  - 协调Agent执行                                          │
│  - 管理数据流                                              │
│  - 错误处理和重试                                          │
└──────────────────────┬────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                   Agent Layer (智能体层)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Explorer │→│Evaluator │→│ Thinker  │→│Organizer│ │
│  └──────────┘  └──────────┘  └──────────┘  └────┬─────┘ │
│                                              ↓            │
│                                      ┌──────────────┐   │
│                                      │  Outputter   │   │
│                                      └──────┬───────┘   │
│                                             ↓             │
│                                      ┌──────────────┐   │
│                                      │ 用户消费     │   │
│                                      └──────────────┘   │
│                                             ↑             │
│                                      ┌──────────────┐   │
│                                      │ 反馈优化     │   │
│                                      └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                 Service Layer (服务层)                      │
├─────────────────────────────────────────────────────────────┤
│  - Database (PostgreSQL + pgvector)                         │
│  - Vector Store (pgvector)                                  │
│  - Cache (Redis)                                             │
│  - Queue (Redis/Celery)                                      │
│  - Storage (S3/Local)                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Organizer Agent详细设计

### 2.1 职责和输入输出

```python
class OrganizerAgent(AgentProtocol):
    """
    整理者 - 知识架构师

    职责:
    1. 将非结构化内容转化为结构化知识
    2. 建立知识图谱，发现隐藏关联
    3. 聚类主题，识别研究热点
    4. 分析时间线，追踪演化
    5. 发现研究gap和机会点

    输入:
    {
        "high_quality": List[Node],      # 高质量节点
        "insights": List[Insight],        # Thinker的洞察
        "existing_graph": Graph,         # 已有的知识图谱
    }

    输出:
    {
        "knowledge_graph": Graph,
        "topics": Dict[str, TopicInfo],
        "timeline": List[Event],
        "trends": TrendsAnalysis,
        "questions": List[Question],
        "clusters": List[Cluster],
        "metrics": Dict
    }
    """
```

### 2.2 核心模块设计

#### 模块1: 知识图谱构建器

```python
class KnowledgeGraphBuilder:
    """知识图谱构建器"""

    def __init__(self, db: Session):
        self.db = db
        self.embedding_model = self._load_embedding_model()

    def build_graph(self, nodes: List[Node], insights: List[Insight]) -> Graph:
        """
        构建知识图谱

        节点类型:
        - Paper: 论文
        - Concept: 概念/术语 (从tags和内容提取)
        - Author: 作者
        - Insight: 洞察
        - Method: 方法论
        - Dataset: 数据集
        - Application: 应用场景

        边类型:
        - cites: Paper → Paper (引用关系)
        - discusses: Paper → Concept (讨论概念)
        - uses: Paper → Method (使用方法)
        - applies_to: Paper → Application (应用)
        - authored_by: Paper → Author (作者)
        - derives_from: Insight → Paper (源自论文)
        - related_to: 任意节点 (语义相关)
        - contradicts: Paper → Paper (矛盾)
        - extends: Paper → Paper (扩展)
        """
        graph = Graph()

        # 1. 添加节点
        for node in nodes:
            graph.add_node("paper", node.id, {
                "title": node.title,
                "content": node.content,
                "tags": node.tags,
                "score": node.value_score
            })

            # 提取并添加概念节点
            concepts = self._extract_concepts(node)
            for concept in concepts:
                graph.add_node("concept", concept, {})
                graph.add_edge(node.id, concept, "discusses")

            # 提取并添加作者节点
            authors = self._extract_authors(node)
            for author in authors:
                graph.add_node("author", author, {})
                graph.add_edge(node.id, author, "authored_by")

        # 2. 添加洞察节点
        for insight in insights:
            graph.add_node("insight", insight.id, {
                "content": insight.insight_content,
                "type": insight.insight_type,
                "score": insight.value_score
            })

            # 连接到源论文
            for source_id in insight.source_node_ids:
                graph.add_edge(insight.id, source_id, "derives_from")

        # 3. 发现语义关联 (基于向量相似度)
        self._add_semantic_edges(graph)

        # 4. 发现引用关系 (如果可用)
        self._add_citation_edges(graph)

        return graph

    def _extract_concepts(self, node: Node) -> List[str]:
        """
        提取概念/术语

        方法:
        1. 从tags获取
        2. 使用NER模型提取
        3. 关键词提取 (TF-IDF)
        """
        concepts = set(node.tags or [])

        # 使用NER提取更多概念
        # (使用spaCy或transformers)
        entities = self._extract_entities(node.content)
        concepts.update(entities)

        # 关键词提取
        keywords = self._extract_keywords(node.content)
        concepts.update(keywords)

        return list(concepts)

    def _add_semantic_edges(self, graph: Graph):
        """
        基于向量相似度添加语义边

        方法:
        1. 对所有节点计算embedding
        2. 计算余弦相似度
        3. 相似度 > 0.75 添加related_to边
        """
        nodes = list(graph.nodes)
        embeddings = self.embedding_model.encode([n.content for n in nodes])

        # 计算相似度矩阵
        similarities = cosine_similarity(embeddings)

        for i, j in enumerate(similarities):
            if similarities[i][j] > 0.75 and i != j:
                graph.add_edge(nodes[i].id, nodes[j].id, "related_to", {
                    "weight": similarities[i][j]
                })
```

**技术选型**:

| 组件 | 选项 | 选择 | 理由 |
|------|------|------|------|
| 向量化 | sentence-transformers, OpenAI Embeddings, spaCy | **sentence-transformers** | 开源、高质量、本地运行 |
| 模型 | `all-MiniLM-L6-v2`, `all-mpnet-base-v2` | **all-MiniLM-L6-v2** | 轻量、快速、中文支持好 |
| NER | spaCy, transformers, HuggingFace | **spaCy + 自定义** | 快速、可扩展 |
| 图数据库 | NetworkX, igraph, Neo4j | **NetworkX + PostgreSQL** | 简单、无需额外服务 |
| 相似度计算 | scikit-learn, faiss | **scikit-learn** | 数据量不大，足够用 |

#### 模块2: 主题聚类器

```python
class TopicClusterer:
    """主题聚类器"""

    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.umap_model = umap.UMAP(n_components=2, random_state=42)
        self.clustering_model = hdbscan.HDBSCAN(min_cluster_size=3)

    def cluster_topics(self, items: List[Union[Node, Insight]]) -> Dict[str, ClusterInfo]:
        """
        聚类主题

        流程:
        1. 文本向量化
        2. UMAP降维到2D
        3. HDBSCAN聚类
        4. 为每个cluster生成主题名称
        """
        # 1. 向量化
        texts = [self._prepare_text(item) for item in items]
        embeddings = self.embedding_model.encode(texts)

        # 2. 降维
        embeddings_2d = self.umap_model.fit_transform(embeddings)

        # 3. 聚类
        labels = self.clustering_model.fit_predict(embeddings)
        unique_labels = set(labels) - {-1}  # 排除噪声点

        # 4. 组织结果
        clusters = {}
        for label in unique_labels:
            indices = [i for i, l in enumerate(labels) if l == label]
            cluster_items = [items[i] for i in indices]

            # 生成主题名称
            topic_name = self._generate_topic_name(cluster_items)

            clusters[topic_name] = ClusterInfo(
                name=topic_name,
                items=cluster_items,
                size=len(cluster_items),
                coherence=self._calculate_coherence(indices, embeddings),
                representative=cluster_items[0] if cluster_items else None
            )

        return clusters

    def _generate_topic_name(self, items: List) -> str:
        """
        为聚类生成主题名称

        方法:
        1. 提取关键词 (TF-IDF)
        2. 使用LLM生成名称 (可选)
        """
        # 提取最频繁的tags
        all_tags = []
        for item in items:
            all_tags.extend(item.tags or [])

        from collections import Counter
        top_tags = [tag for tag, _ in Counter(all_tags).most_common(3)]

        # 简单组合
        if len(top_tags) >= 2:
            return f"{top_tags[0]} & {top_tags[1]}"
        elif top_tags:
            return top_tags[0]
        else:
            return "Unknown Topic"

    def _calculate_coherence(self, indices, embeddings):
        """计算聚类内聚度"""
        if len(indices) < 2:
            return 1.0

        cluster_embeddings = embeddings[indices]
        centroid = cluster_embeddings.mean(axis=0)

        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(cluster_embeddings, [centroid])

        return similarities.mean()
```

**技术选型**:

| 组件 | 选项 | 选择 | 理由 |
|------|------|------|------|
| 向量化 | sentence-transformers | **all-MiniLM-L6-v2** | 轻量、中文好 |
| 降维 | UMAP, t-SNE, PCA | **UMAP** | 保留全局结构、快速 |
| 聚类 | HDBSCAN, K-Means, DBSCAN | **HDBSCAN** | 无需预设数量、处理噪声 |
| 关键词 | TF-IDF, YAKE, RAKE | **TF-IDF** | 简单有效 |

#### 模块3: 时间线分析器

```python
class TimelineAnalyzer:
    """时间线分析器"""

    def analyze_timeline(self, items: List[Node]) -> List[Event]:
        """
        构建时间线，识别关键事件

        方法:
        1. 按日期排序
        2. 识别"热点" (短时间内多篇高质量论文)
        3. 识别"突破" (新概念、新方法出现)
        4. 构建事件时间线
        """
        # 按日期分组
        by_date = defaultdict(list)
        for item in items:
            date = item.discovered_at.date()
            by_date[date].append(item)

        # 识别热点
        events = []
        for date, date_items in sorted(by_date.items()):
            if len(date_items) >= 3:  # 热点阈值
                # 这是一个热点日期
                event = Event(
                    date=date,
                    type="hotspot",
                    description=f"{len(date_items)}篇论文发布",
                    items=[i.id for i in date_items],
                    impact=self._calculate_impact(date_items)
                )
                events.append(event)

        # 识别趋势
        events.extend(self._identify_trends(by_date))

        # 按时间排序
        events.sort(key=lambda e: e.date)

        return events

    def _identify_trends(self, by_date: Dict[date, List]) -> List[Event]:
        """
        识别趋势变化

        方法:
        1. 按周统计关键词频率
        2. 计算频率变化率
        3. 识别上升/下降/新兴趋势
        """
        # 按周统计
        weekly_keywords = defaultdict(Counter)
        for date, items in by_date.items():
            week = self._get_week_number(date)
            for item in items:
                for tag in item.tags or []:
                    weekly_keywords[week][tag] += 1

        weeks = sorted(weekly_keywords.keys())

        # 计算趋势
        trends = []
        for tag in self._get_all_tags(weekly_keywords):
            frequencies = [weekly_keywords[w][tag] for w in weeks]

            # 计算变化率
            if len(frequencies) >= 2:
                recent_avg = sum(frequencies[-2:]) / 2
                earlier_avg = sum(frequencies[:-2]) / len(frequencies[:-2]) if len(frequencies) > 2 else 0

                if recent_avg > earlier_avg * 1.5:
                    trends.append(Event(
                        date=weeks[-1],
                        type="trend_rising",
                        description=f"'{tag}'热度上升 {((recent_avg - earlier_avg) / earlier_avg * 100):.0f}%",
                        trend_type="rising",
                        keyword=tag
                    ))
                elif recent_avg < earlier_avg * 0.7:
                    trends.append(Event(
                        date=weeks[-1],
                        type="trend_declining",
                        description=f"'{tag}'关注度下降",
                        trend_type="declining",
                        keyword=tag
                    ))

        return trends
```

**技术选型**:

| 组件 | 选项 | 选择 | 理由 |
|------|------|------|------|
| 时间序列 | Pandas, NumPy | **Pandas** | 时间序列处理简单 |
| 统计 | SciPy, statsmodels | **SciPy** | 统计检验 |
| 趋势检测 | Mann-Kendall,CUSUM | **简单比例** | 直观易懂 |

#### 模块4: 问题发现器

```python
class QuestionDiscoverer:
    """问题发现器"""

    def discover_questions(self, graph: Graph, topics: Dict) -> List[Question]:
        """
        从知识图谱中发现问题

        识别类型:
        1. Research Gap: 未被研究过的交叉点
        2. Contradiction: 结论矛盾的论文
        3. Opportunity: A方法可应用于B领域
        4. Missing Link: 理论上应该有关联但实际没有
        """
        questions = []

        # 1. 发现交叉点机会
        questions.extend(self._find_intersection_opportunities(graph))

        # 2. 发现矛盾点
        questions.extend(self._find_contradictions(graph))

        # 3. 发现应用机会
        questions.extend(self._find_application_opportunities(graph))

        # 4. 发现研究空白
        questions.extend(self._find_research_gaps(graph, topics))

        return questions

    def _find_intersection_opportunities(self, graph: Graph) -> List[Question]:
        """
        发现交叉点机会

        方法:
        1. 找到两个不直接连接但语义相关的概念
        2. 检查是否有人研究它们的结合
        """
        opportunities = []

        # 获取所有概念节点
        concepts = [n for n in graph.nodes if n.type == "concept"]

        # 计算概念共现
        for c1, c2 in combinations(concepts, 2):
            # 检查是否直接连接
            if not graph.has_edge(c1, c2):
                # 检查是否有共同邻居
                neighbors1 = set(graph.neighbors(c1))
                neighbors2 = set(graph.neighbors(c2))

                common = neighbors1 & neighbors2

                if len(common) > 0:
                    # 有共同邻居但直接无连接 → 机会
                    opportunities.append(Question(
                        question=f"'{c1.label}'和'{c2.label}'的结合应用未被研究",
                        type="intersection_opportunity",
                        context=list(common),
                        importance="medium",
                        suggested_exploration=f"{c1.label} {c2.label}"
                    ))

        return opportunities

    def _find_contradictions(self, graph: Graph) -> List[Question]:
        """
        发现矛盾点

        方法:
        1. 找到讨论相同概念但结论相反的论文
        2. 使用LLM判断是否矛盾
        """
        contradictions = []

        # 按概念分组论文
        concept_papers = defaultdict(list)
        for node in graph.nodes:
            if node.type == "paper":
                for concept in graph.neighbors(node):
                    if concept.type == "concept":
                        concept_papers[concept.id].append(node)

        # 对于有3篇以上论文的概念
        for concept_id, papers in concept_papers.items():
            if len(papers) >= 3:
                # 使用LLM分析是否存在矛盾
                contradiction = self._check_contradiction(papers)
                if contradiction:
                    contradictions.append(Question(
                        question=f"关于'{concept_id}'的研究存在矛盾",
                        type="contradiction",
                        context=papers,
                        importance="high"
                    ))

        return contradictions
```

---

## 3. Outputter Agent详细设计

### 3.1 职责和输入输出

```python
class OutputterAgent(AgentProtocol):
    """
    输出者 - 报告生成器

    职责:
    1. 将结构化知识转化为用户可消费的内容
    2. 生成多种格式的报告（日报、周报、洞察简报）
    3. 创建可视化图表
    4. 生成反馈给探索者的新方向

    输入:
    {
        "knowledge_graph": Graph,
        "topics": Dict[str, TopicInfo],
        "timeline": List[Event],
        "trends": TrendsAnalysis,
        "questions": List[Question],
    }

    输出:
    {
        "daily_report": str,
        "weekly_summary": str,
        "insight_briefs": List[str],
        "recommendations": List[str],
        "visualizations": Dict[str, Visualization],
        "feedback_to_explorer": List[str],
    }
    """
```

### 3.2 核心模块设计

#### 模块1: 报告生成器

```python
class ReportGenerator:
    """报告生成器"""

    def generate_daily_report(self, data: Dict) -> str:
        """
        生成日报

        格式: Markdown
        内容:
        1. 数据摘要
        2. 今日亮点
        3. 趋势
        4. 洞察
        5. 明日建议
        """
        report = []
        report.append(f"# 知识探索日报 - {datetime.now().strftime('%Y-%m-%d')}\n")

        # 1. 数据摘要
        report.append("## 📊 今日数据\n")
        stats = self._calculate_daily_stats(data)
        report.append(f"- 新发现: {stats['new_items']} 篇")
        report.append(f"- 高质量: {stats['high_quality']} 篇")
        report.append(f"- 洞察: {stats['insights']} 条\n")

        # 2. 今日亮点
        highlights = self._extract_highlights(data)
        if highlights:
            report.append("## 🔥 今日亮点\n")
            for highlight in highlights[:3]:  # 最多3个
                report.append(f"### {highlight['title']}\n")
                report.append(f"{highlight['description']}\n")
                if highlight.get('impact'):
                    report.append(f"**影响**: {highlight['impact']}\n")
                if highlight.get('suggestion'):
                    report.append(f"**建议**: {highlight['suggestion']}\n")
                report.append("\n")

        # 3. 趋势
        if data.get('trends'):
            report.append("## 📈 趋势\n")
            trends = data['trends']
            if trends.get('rising'):
                report.append(f"- 🔼 **上升**: {', '.join(trends['rising'][:3])}")
            if trends.get('emerging'):
                report.append(f"- ✨ **新兴**: {', '.join(trends['emerging'][:3])}")
            if trends.get('declining'):
                report.append(f"- 🔽 **下降**: {', '.join(trends['declining'][:3])}")
            report.append("\n")

        # 4. 洞察
        if data.get('insights'):
            report.append("## 💡 洞察\n")
            for insight in data['insights'][:3]:
                report.append(f"### {insight['title']}\n")
                report.append(f"{insight['content']}\n")
                report.append(f"**来源**: {insight['source']}\n\n")

        # 5. 明日建议
        feedback = self._generate_feedback(data)
        if feedback:
            report.append("## 🎯 明日建议\n")
            for i, suggestion in enumerate(feedback[:3], 1):
                report.append(f"{i}. {suggestion}")
            report.append("\n")

        return "".join(report)

    def generate_weekly_summary(self, data: Dict) -> str:
        """
        生成周报

        格式: Markdown
        内容:
        1. 本周核心主题
        2. 重要进展
        3. 关联发现
        4. 下周预测
        """
        report = []
        report.append(f"# 本周知识总结 - Week {datetime.now().isocalendar()[1]}\n")

        # 1. 核心主题
        topics = data.get('topics', {})
        if topics:
            report.append("## 🎯 核心主题\n")

            # 按大小排序
            sorted_topics = sorted(topics.items(), key=lambda x: -x[1].size)

            for i, (topic_name, topic_info) in enumerate(sorted_topics[:5], 1):
                report.append(f"### {i}. {topic_name} ({topic_info.size}篇)")
                if topic_info.representative:
                    report.append(f"**代表**: {topic_info.representative.title[:60]}...")
                if topic_info.coherence:
                    report.append(f"**内聚度**: {topic_info.coherence:.2f}")
                report.append("")

        # 2. 时间线
        timeline = data.get('timeline', [])
        if timeline:
            report.append("## 📅 本周时间线\n")
            for event in timeline:
                report.append(f"**{event.date}**: {event.description}")
                if event.impact:
                    report.append(f" (影响: {event.impact})")
                report.append("")

        # 3. 关联发现
        graph = data.get('knowledge_graph')
        if graph:
            connections = self._find_important_connections(graph)
            if connections:
                report.append("## 🔗 重要关联\n")
                for conn in connections[:5]:
                    report.append(f"- {conn['source']}")
                    report.append(f"  → {conn['target']}")
                    report.append(f"  ({conn['relation']})")
                    report.append("")

        # 4. 下周预测
        predictions = self._make_predictions(data)
        if predictions:
            report.append("## 🔮 下周预测\n")
            for prediction in predictions:
                report.append(f"- {prediction}")
            report.append("")

        return "".join(report)
```

**技术选型**:

| 组件 | 选项 | 选择 | 理由 |
|------|------|------|------|
| 模板引擎 | Jinja2, Mako, StringTemplate | **Jinja2** | 功能强大、熟悉 |
| Markdown | markdown, markdown2 | **markdown2** | 扩展性好 |
| 邮件发送 | SMTP, SendGrid, AWS SES | **SMTP + SendGrid** | 灵活 |
| 调度 | schedule, APScheduler | **schedule** | 简单轻量 |

#### 模块2: 可视化生成器

```python
class VisualizationGenerator:
    """可视化生成器"""

    def __init__(self):
        self.output_dir = Path("visualizations")
        self.output_dir.mkdir(exist_ok=True)

    def generate_all(self, data: Dict) -> Dict[str, str]:
        """
        生成所有可视化

        返回:
        {
            "knowledge_graph": "path/to/network.html",
            "topic_clusters": "path/to/clusters.html",
            "timeline": "path/to/timeline.html",
            "trends": "path/to/trends.png",
        }
        """
        visualizations = {}

        # 1. 知识图谱
        visualizations["knowledge_graph"] = self._generate_knowledge_graph(
            data["knowledge_graph"]
        )

        # 2. 主题聚类
        if "topics" in data:
            visualizations["topic_clusters"] = self._generate_topic_clusters(
                data["topics"]
            )

        # 3. 时间线
        if "timeline" in data:
            visualizations["timeline"] = self._generate_timeline(
                data["timeline"]
            )

        # 4. 趋势图
        if "trends" in data:
            visualizations["trends"] = self._generate_trend_chart(
                data["trends"]
            )

        return visualizations

    def _generate_knowledge_graph(self, graph: Graph) -> str:
        """
        生成交互式知识图谱

        技术: PyVis + HTML
        """
        import networkx as nx
        from pyvis.network import Network
        import networkx as nx

        # 转换为NetworkX图
        nx_graph = nx.Graph()

        # 添加节点
        for node in graph.nodes:
            nx_graph.add_node(node.id,
                label=node.label,
                title=node.type,
                color=self._get_color_by_type(node.type),
                size=self._get_size_by_importance(node)
            )

        # 添加边
        for edge in graph.edges:
            nx_graph.add_edge(
                edge.source,
                edge.target,
                title=edge.label,
                width=edge.weight or 1
            )

        # 使用PyVis生成交互图
        net = Network(height="750px", width="100%", notebook=False)
        net.from_nx(nx_graph)
        net.toggle_physics(True)

        output_path = self.output_dir / "knowledge_graph.html"
        net.save_graph(str(output_path))

        return str(output_path)

    def _generate_topic_clusters(self, topics: Dict) -> str:
        """
        生成主题聚类可视化

        技术: Plotly Scatter Plot
        """
        import plotly.graph_objects as go
        import plotly.express as px

        # 准备数据
        clusters_data = []
        for topic_name, topic_info in topics.items():
            # 获取2D坐标
            for item in topic_info.items:
                clusters_data.append({
                    "x": item.embedding_2d[0],
                    "y": item.embedding_2d[1],
                    "topic": topic_name,
                    "title": item.title[:50]
                })

        df = pd.DataFrame(clusters_data)

        # 创建散点图
        fig = px.scatter(
            df,
            x="x",
            y="y",
            color="topic",
            hover_data=["title"],
            title="知识主题聚类"
        )

        output_path = self.output_dir / "topic_clusters.html"
        fig.write_html(str(output_path))

        return str(output_path)
```

**技术选型**:

| 组件 | 选项 | 选择 | 理由 |
|------|------|------|------|
| 图可视化 | PyVis, D3.js, Cytoscape.js | **PyVis** | Python原生、简单 |
| 散点图 | Plotly, Matplotlib, Seaborn | **Plotly** | 交互性好 |
| 图表 | Plotly, Matplotlib, Altair | **Plotly** | 统一使用 |
| 降维展示 | Plotly, Matplotlib | **Plotly** | 动画支持 |

#### 模块3: 反馈生成器

```python
class FeedbackGenerator:
    """反馈生成器"""

    def generate_feedback(self, data: Dict) -> List[str]:
        """
        为探索者生成反馈

        反馈类型:
        1. 新探索方向: 基于趋势和关联
        2. 优化建议: 基于当前系统状态
        3. 优先级调整: 基于用户反馈
        """
        feedback = []

        # 1. 从趋势生成新方向
        if "trends" in data:
            trends = data["trends"]
            if trends.get("rising"):
                for rising_topic in trends["rising"][:2]:
                    feedback.append(
                        f"检测到'{rising_topic}'热度上升，建议深度探索"
                    )
            if trends.get("emerging"):
                feedback.append(
                    f"发现新兴主题: {trends['emerging'][0]}，建议关注"
                )

        # 2. 从关联生成新方向
        if "questions" in data:
            for question in data["questions"][:3]:
                if question.type == "intersection_opportunity":
                    feedback.append(
                        f"交叉机会: {question.suggested_exploration}"
                    )

        # 3. 从知识图谱生成新方向
        if "knowledge_graph" in data:
            graph = data["knowledge_graph"]

            # 找到高度连接的节点（中心概念）
            central_nodes = self._find_central_nodes(graph)
            for node in central_nodes[:2]:
                feedback.append(
                    f"中心概念'{node.label}'已有{len(list(graph.neighbors(node)))}篇研究，"
                    f"可以考虑其应用场景"
                )

        return feedback
```

---

## 4. 技术栈选型

### 4.1 向量和语义处理

```python
# requirements.txt
sentence-transformers==2.2.2      # 文本向量化
scikit-learn==1.3.0              # 相似度计算、聚类
umap-learn==0.5.3                # UMAP降维
hdbscan==0.8.29                 # HDBSCAN聚类
spacy==3.7.2                     # NER（可选，中文用hanlp）
```

**选择理由**:
- `sentence-transformers`: 开源、质量高、中文支持好
- `all-MiniLM-L6-v2`: 轻量级（420MB）、速度快、中文友好
- `UMAP`: 保留全局结构，比t-SNE快
- `HDBSCAN`: 无需预设聚类数量、处理噪声、识别离群点

### 4.2 图数据处理

```python
# requirements.txt
networkx==3.2.1                  # 图操作
pyvis==0.3.2                      # 图可视化
plotly==5.18.0                    # 交互式图表
pandas==2.1.4                    # 数据处理
numpy==1.26.0                     # 数值计算
```

**选择理由**:
- `NetworkX`: Python标准、简单易用
- `PyVis`: 快速生成交互式图、支持物理模拟
- `Plotly`: 交互式图表、支持导出HTML

### 4.3 NLP和文本处理

```python
# requirements.txt
jieba==0.42.1                     # 中文分词
hanlp==2.1.0                      # 中文NLP（可选）
openai==1.12.0                     # 如果使用OpenAI API
anthropic==0.18.1                 # 如果使用Claude API
zhipuai==1.0.0                     # 如果使用智谱AI
```

**选择策略**:
- 基础NLP: jieba（中文分词）、NLTK（英文）
- 高级NLP: spaCy（NER）、HanLP（中文）
- AI调用: 使用现有的Evaluator配置

### 4.4 报告生成

```python
# requirements.txt
jinja2==3.1.3                     # 模板引擎
markdown2==2.4.1                   # Markdown处理
python-dateutil==2.8.2            # 日期处理
pytz==2023.3                      # 时区处理
```

### 4.5 数据库模型扩展

```sql
-- 新增表结构

-- 1. 知识图谱节点表
CREATE TABLE knowledge_nodes (
    id SERIAL PRIMARY KEY,
    node_type VARCHAR(50) NOT NULL,  -- paper, concept, author, insight, method
    label TEXT NOT NULL,
    data JSONB,                       -- 节点属性
    embedding VECTOR(384),           -- 向量表示
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_type (node_type),
    INDEX idx_label (label)
);

-- 2. 知识图谱边表
CREATE TABLE knowledge_edges (
    id SERIAL PRIMARY KEY,
    source_node_id INTEGER NOT NULL,
    target_node_id INTEGER NOT NULL,
    edge_type VARCHAR(50) NOT NULL,  -- cites, discusses, related_to, etc.
    weight FLOAT DEFAULT 1.0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (source_node_id) REFERENCES knowledge_nodes(id),
    FOREIGN KEY (target_node_id) REFERENCES knowledge_nodes(id),
    INDEX idx_source (source_node_id),
    INDEX idx_target (target_node_id),
    INDEX idx_type (edge_type)
);

-- 3. 主题聚类表
CREATE TABLE topic_clusters (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    cluster_id INTEGER,                  -- HDBSCAN分配的ID
    coherence FLOAT,
    representative_id INTEGER,           -- 代表性节点
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_name (name)
);

-- 4. 节点-聚类关联表
CREATE TABLE node_cluster_membership (
    node_id INTEGER NOT NULL,
    cluster_id INTEGER NOT NULL,
    confidence FLOAT,
    FOREIGN KEY (node_id) REFERENCES knowledge_nodes(id),
    FOREIGN KEY (cluster_id) REFERENCES topic_clusters(id),
    PRIMARY KEY (node_id, cluster_id)
);

-- 5. 时间事件表
CREATE TABLE timeline_events (
    id SERIAL PRIMARY KEY,
    event_date DATE NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- hotspot, breakthrough, trend
    description TEXT NOT NULL,
    impact TEXT,
    related_nodes INTEGER[],
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_date (event_date),
    INDEX idx_type (event_type)
);

-- 6. 趋势数据表
CREATE TABLE trend_metrics (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    frequency INTEGER NOT NULL,
    trend_type VARCHAR(20),               -- rising, stable, declining, emerging
    change_rate FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_keyword (keyword),
    INDEX idx_date (date)
);

-- 7. 研究问题表
CREATE TABLE research_questions (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,  -- research_gap, contradiction, opportunity
    context JSONB,
    importance VARCHAR(20),             -- high, medium, low
    status VARCHAR(20) DEFAULT 'open',    -- open, addressed, rejected
    suggested_exploration TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_type (question_type),
    INDEX idx_status (status),
    INDEX idx_importance (importance)
);

-- 8. 生成的报告表
CREATE TABLE generated_reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(20) NOT NULL,   -- daily, weekly, insight
    content TEXT NOT NULL,
    format VARCHAR(20) DEFAULT 'markdown', -- markdown, html
    date_range DATE_RANGE,
    metrics JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_type (report_type),
    INDEX idx_date (date_range)
);
```

---

## 5. 数据模型设计

### 5.1 Organizer Agent数据模型

```python
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, JSON, ForeignKey, Date
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship

class KnowledgeNode(Base):
    """知识图谱节点"""
    __tablename__ = "knowledge_nodes"

    id = Column(Integer, primary_key=True)
    node_type = Column(String(50), nullable=False, index=True)
    label = Column(Text, nullable=False)
    data = Column(JSONB)
    embedding = Column(Vector(384))  # all-MiniLM-L6-v2维度
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    edges_as_source = relationship("KnowledgeEdge", foreign_keys=["source_node_id"])
    edges_as_target = relationship("KnowledgeEdge", foreign_keys=["target_node_id"])

class KnowledgeEdge(Base):
    """知识图谱边"""
    __tablename__ = "knowledge_edges"

    id = Column(Integer, primary_key=True)
    source_node_id = Column(Integer, ForeignKey("knowledge_nodes.id"), nullable=False)
    target_node_id = Column(Integer, ForeignKey("knowledge_nodes.id"), nullable=False)
    edge_type = Column(String(50), nullable=False)
    weight = Column(Float, default=1.0)
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

class TopicCluster(Base):
    """主题聚类"""
    __tablename__ = "topic_clusters"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    cluster_id = Column(Integer)
    coherence = Column(Float)
    representative_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    nodes = relationship("NodeClusterMembership", back_populates="cluster")

class NodeClusterMembership(Base):
    """节点-聚类关联"""
    __tablename__ = "node_cluster_membership"

    node_id = Column(Integer, ForeignKey("knowledge_nodes.id"), primary_key=True)
    cluster_id = Column(Integer, ForeignKey("topic_clusters.id"), primary_key=True)
    confidence = Column(Float)

class TimelineEvent(Base):
    """时间线事件"""
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True)
    event_date = Column(Date, nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    impact = Column(Text)
    related_nodes = Column(ARRAY(Integer))
    created_at = Column(DateTime, default=datetime.utcnow)

class TrendMetric(Base):
    """趋势指标"""
    __tablename__ = "trend_metrics"

    id = Column(Integer, primary_key=True)
    keyword = Column(String(100), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    frequency = Column(Integer, nullable=False)
    trend_type = Column(String(20))  # rising, stable, declining, emerging
    change_rate = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class ResearchQuestion(Base):
    """研究问题"""
    __tablename__ = "research_questions"

    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False, index=True)
    context = Column(JSONB)
    importance = Column(String(20), index=True)
    status = Column(String(20), default="open", index=True)
    suggested_exploration = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 5.2 Outputter Agent数据模型

```python
class GeneratedReport(Base):
    """生成的报告"""
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True)
    report_type = Column(String(20), nullable=False, index=True)  # daily, weekly, insight
    content = Column(Text, nullable=False)
    format = Column(String(20), default="markdown")
    date_range = Column(String(50))  # e.g., "2025-12-23 to 2025-12-29"
    metrics = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
```

---

## 6. API接口设计

### 6.1 Organizer Agent API

```python
# API endpoints

@router.post("/api/v2/organizer/build_graph")
async def build_knowledge_graph(
    node_ids: List[int],
    db: Session = Depends(get_db)
):
    """
    构建知识图谱

    请求:
    {
        "node_ids": [1, 2, 3, ...]
    }

    响应:
    {
        "graph_id": 123,
        "nodes_count": 45,
        "edges_count": 120,
        "build_time": 2.3
    }
    """
    pass

@router.post("/api/v2/organizer/cluster_topics")
async def cluster_topics(
    node_ids: List[int],
    db: Session = Depends(get_db)
):
    """
    主题聚类

    请求:
    {
        "node_ids": [1, 2, 3, ...],
        "algorithm": "hdbscan"
    }

    响应:
    {
        "clusters": [
            {
                "name": "Federated Learning",
                "size": 8,
                "coherence": 0.85,
                "items": [1, 5, 9, ...]
            },
            ...
        ]
    }
    """
    pass

@router.post("/api/v2/organizer/analyze_timeline")
async def analyze_timeline(
    node_ids: List[int],
    db: Session = Depends(get_db)
):
    """
    时间线分析

    响应:
    {
        "events": [
            {
                "date": "2025-12-29",
                "type": "hotspot",
                "description": "5篇论文发布"
            },
            ...
        ]
    }
    """
    pass

@router.post("/api/v2/organizer/discover_questions")
async def discover_questions(
    graph_id: int,
    db: Session = Depends(get_db)
):
    """
    发现研究问题

    响应:
    {
        "questions": [
            {
                "question": "联邦学习在医疗数据中的应用效果如何？",
                "type": "opportunity",
                "importance": "high"
            },
            ...
        ]
    }
    """
    pass
```

### 6.2 Outputter Agent API

```python
@router.post("/api/v2/outputter/generate_report")
async def generate_report(
    report_type: str,  # daily, weekly, insight
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    生成报告

    响应:
    {
        "report_id": 456,
        "content": "...markdown...",
        "visualizations": {
            "knowledge_graph": "/visualizations/graph_123.html",
            "trends": "/visualizations/trends_123.png"
        }
    }
    """
    pass

@router.get("/api/v2/outputter/reports")
async def get_reports(
    report_type: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """获取报告列表"""
    pass

@router.get("/api/v2/outputter/reports/{report_id}")
async def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """获取报告详情"""
    pass
```

---

## 7. 实施指南

### 7.1 Phase 1: Organizer Agent核心功能 (Week 1-2)

**Week 1: 知识图谱构建**
- [ ] Day 1-2: 数据库模型创建和迁移
- [ ] Day 3-4: 向量化服务实现
- [ ] Day 5-7: 图构建逻辑实现
- [ ] 测试: 构建一个包含50个节点的图

**Week 2: 聚类和分析**
- [ ] Day 1-2: UMAP+HDBSCAN聚类实现
- [ ] Day 3-4: 时间线分析实现
- [ ] Day 5-7: 问题发现实现
- [ ] 测试: 端到端测试

### 7.2 Phase 2: Outputter Agent核心功能 (Week 3-4)

**Week 3: 报告生成**
- [ ] Day 1-2: 模板设计和实现
- [ ] Day 3-4: 日报生成器
- [ ] Day 5-7: 周报生成器
- [ ] 测试: 生成完整报告

**Week 4: 可视化**
- [ ] Day 1-2: 知识图谱可视化
- [ ] Day 3-4: 主题聚类可视化
- [ ] Day 5-7: 趋势图表
- [ ] 测试: 生成交互式HTML

### 7.3 依赖安装

```bash
# 创建虚拟环境
cd backend
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 新增v2.0依赖
pip install sentence-transformers==2.2.2
pip install umap-learn==0.5.3
pip install hdbscan==0.8.29
pip install networkx==3.2.1
pip install pyvis==0.3.2
pip install plotly==5.18.0
pip install jieba==0.42.1
```

### 7.4 环境配置

```bash
# backend/.env 新增配置

# Embedding模型配置
EMBEDDING_MODEL=sentence-transformers
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
EMBEDDING_CACHE_DIR=./cache/models

# 聚类配置
CLUSTERING_ALGORITHM=hdbscan
CLUSTERING_MIN_CLUSTER_SIZE=3
CLUSTERING_MIN_SAMPLES=5

# 可视化配置
VISUALIZATION_DIR=./visualizations
VISUALIZATION_FORMAT=html

# 报告配置
REPORT_TEMPLATE_DIR=./templates
REPORT_OUTPUT_DIR=./reports
REPORT_SEND_EMAIL_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
```

---

## 附录

### A. 性能估算

| 操作 | 数据量 | 预估时间 |
|------|--------|----------|
| 向量化100篇论文 | 100篇 | ~10秒 |
| 构建知识图谱 | 100节点 | ~5秒 |
| UMAP降维 | 100节点 | ~3秒 |
| HDBSCAN聚类 | 100节点 | ~2秒 |
| 生成日报 | - | ~2秒 |
| 生成可视化 | - | ~5秒 |
| **总计** | **100篇** | **~30秒** |

### B. 存储估算

| 数据类型 | 每100篇 | 每1000篇 |
|---------|--------|----------|
| 向量存储 | ~150MB | ~1.5GB |
| 图节点 | ~50KB | ~500KB |
| 图边 | ~200KB | ~2MB |
| 可视化HTML | ~1MB | ~10MB |

### C. 技术债务和风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Embedding模型加载慢 | 启动延迟 | 模型缓存、懒加载 |
| 大规模图性能下降 | 超过1000节点 | 分片、使用图数据库 |
| 中文NLP准确度低 | 概念提取不准 | 使用HanLP、持续训练 |
| LLM调用成本高 | 洞察生成贵 | 缓存、批量处理 |

---

**文档维护**: 随实施进展持续更新
