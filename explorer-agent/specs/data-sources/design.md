# Design - Data Sources (数据源)

## Architecture Overview

### Component Design
```
┌─────────────────────────────────────────┐
│          DataSource (ABC)               │
│  - search(query, num_results)           │
│  - 标准化接口                            │
└──────────────┬──────────────────────────┘
               │
      ┌────────┼────────────────┐
      │        │                │
┌─────▼─────┐ ┌▼──────────┐ ┌──▼─────────┐
│ ArxivSource│ │DuckDuckGo │ │RedditSource│
│ (Academic) │ │ (General) │ │ (Community)│
└───────────┘ └───────────┘ └────────────┘
      │            │               │
┌─────▼─────┐ ┌──▼────────┐ ┌────▼──────┐
│HackerNews │ │GitHubTrend│ │StackOverflow│
│ (Tech)    │ │  (OpenSource)│ │ (Q&A)    │
└───────────┘ └───────────┘ └───────────┘
```

## Component Design

### 1. DataSource (抽象基类)

**职责**: 定义统一的数据源接口

**接口定义**:
```python
from abc import ABC, abstractmethod
from typing import List, Dict

class DataSource(ABC):
    """数据源抽象基类"""

    def __init__(self, name: str, source_type: str):
        self.name = name
        self.source_type = source_type

    @abstractmethod
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """搜索内容
        Args:
            query: 搜索查询
            num_results: 返回结果数量
        Returns:
            标准化结果列表: [
                {
                    "title": str,      # 标题
                    "content": str,    # 内容/摘要
                    "source": str,     # 来源URL
                    "type": str        # 内容类型
                }
            ]
        """
        pass

    @abstractmethod
    def _normalize_results(self, raw_results: any) -> List[Dict]:
        """标准化原始结果"""
        pass
```

### 2. ArxivSource (学术论文)

**职责**: 从Arxiv搜索学术论文

**实现**:
```python
import arxiv

class ArxivSource(DataSource):
    """Arxiv论文数据源"""

    def __init__(self):
        super().__init__("arxiv", "academic")

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """搜索Arxiv论文"""
        results = []

        try:
            # 使用arxiv API搜索
            search = arxiv.Search(
                query=query,
                max_results=num_results,
                sort_by=arxiv.SortCriterion.Relevance
            )

            for result in search.results():
                results.append({
                    "title": result.title,
                    "content": result.summary,
                    "source": result.entry_id,
                    "type": "paper",
                    "metadata": {
                        "authors": [a.name for a in result.authors],
                        "published": result.published.strftime('%Y-%m-%d'),
                        "pdf_url": result.pdf_url
                    }
                })

        except Exception as e:
            logger.error(f"Arxiv search failed: {e}")

        return results

    def _normalize_results(self, raw_results):
        # 结果已在search()中标准化
        return raw_results
```

### 3. DuckDuckGoSource (通用搜索)

**职责**: 从DuckDuckGo进行通用搜索

**实现**:
```python
from duckduckgo_search import DDGS

class DuckDuckGoSource(DataSource):
    """DuckDuckGo通用搜索"""

    def __init__(self):
        super().__init__("duckduckgo", "general")

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """DuckDuckGo搜索"""
        results = []

        try:
            ddgs = DDGS()
            search_results = ddgs.text(
                query,
                max_results=num_results
            )

            for r in search_results:
                results.append({
                    "title": r.get('title', ''),
                    "content": r.get('body', ''),
                    "source": r.get('link', ''),
                    "type": "article"
                })

        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")

        return results

    def _normalize_results(self, raw_results):
        return raw_results
```

### 4. RedditSource (社区讨论)

**职责**: 从Reddit搜索讨论

**实现**:
```python
import requests

class RedditSource(DataSource):
    """Reddit讨论数据源"""

    def __init__(self):
        super().__init__("reddit", "community")
        self.base_url = "https://www.reddit.com/r"

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """搜索Reddit讨论"""
        results = []

        try:
            # 搜索多个subreddit
            subreddits = ["technology", "science", "MachineLearning", "programming"]

            for sub in subreddits:
                url = f"{self.base_url}/{sub}/search.json"
                params = {
                    "q": query,
                    "restrict_sr": "on",
                    "limit": num_results // len(subreddits)
                }

                response = requests.get(url, params=params, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])

                    for post in posts:
                        post_data = post.get('data', {})
                        results.append({
                            "title": post_data.get('title', ''),
                            "content": post_data.get('selftext', ''),
                            "source": f"https://reddit.com{post_data.get('permalink', '')}",
                            "type": "post"
                        })

                if len(results) >= num_results:
                    break

        except Exception as e:
            logger.error(f"Reddit search failed: {e}")

        return results[:num_results]

    def _normalize_results(self, raw_results):
        return raw_results
```

### 5. HackerNewsSource (技术新闻)

**职责**: 从HackerNews获取技术新闻

**实现**:
```python
class HackerNewsSource(DataSource):
    """HackerNews技术新闻"""

    def __init__(self):
        super().__init__("hackernews", "tech_news")
        self.api_base = "https://hacker-news.firebaseio.com/v0"

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """搜索HackerNews（按关键词）"""
        results = []

        try:
            # 获取最新故事
            stories_url = f"{self.api_base}/newstories.json"
            story_ids = requests.get(stories_url).json()

            # 获取前N个故事
            for story_id in story_ids[:num_results * 2]:
                item_url = f"{self.api_base}/item/{story_id}.json"
                item = requests.get(item_url).json()

                # 简单的关键词匹配
                title = item.get('title', '').lower()
                if query.lower() in title:
                    results.append({
                        "title": item.get('title', ''),
                        "content": item.get('text', ''),
                        "source": item.get('url', ''),
                        "type": "news"
                    })

                if len(results) >= num_results:
                    break

        except Exception as e:
            logger.error(f"HackerNews search failed: {e}")

        return results

    def _normalize_results(self, raw_results):
        return raw_results
```

## SourceManager (源管理器)

**职责**: 管理多个数据源，智能选择源

```python
class SourceManager:
    """数据源管理器"""

    def __init__(self):
        self.sources = {
            'arxiv': ArxivSource(),
            'duckduckgo': DuckDuckGoSource(),
            'reddit': RedditSource(),
            'hackernews': HackerNewsSource(),
            # ... 其他源
        }

    def search(self, query: str, num_results: int = 5, source_hint: str = None) -> List[Dict]:
        """搜索多个源

        Args:
            query: 搜索查询
            num_results: 总结果数
            source_hint: 源提示 (可选)

        Returns:
            合并的搜索结果
        """
        # 1. 选择源
        sources = self._select_sources(query, source_hint)

        # 2. 并发搜索
        all_results = []
        for source in sources:
            try:
                results = source.search(query, num_results // len(sources))
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Source {source.name} failed: {e}")

        # 3. 去重
        unique_results = self._deduplicate(all_results)

        return unique_results[:num_results]

    def _select_sources(self, query: str, hint: str = None) -> List[DataSource]:
        """智能选择数据源"""
        if hint:
            # 用户指定源
            return [self.sources.get(hint, ArxivSource())]

        # 根据查询特征选择
        query_lower = query.lower()

        # 学术关键词
        academic_keywords = ['paper', 'research', 'study', 'arxiv', 'theory']
        if any(kw in query_lower for kw in academic_keywords):
            return [self.sources['arxiv']]

        # 技术关键词
        tech_keywords = ['programming', 'code', 'api', 'framework', 'library']
        if any(kw in query_lower for kw in tech_keywords):
            return [
                self.sources['hackernews'],
                self.sources['reddit'],
                self.sources['duckduckgo']
            ]

        # 默认：所有源
        return list(self.sources.values())

    def _deduplicate(self, results: List[Dict]) -> List[Dict]:
        """基于URL去重"""
        seen_urls = set()
        unique = []

        for result in results:
            url = result.get('source', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(result)

        return unique
```

## Performance Optimization

### 优化1: 并发搜索
```python
import asyncio

async def search_multiple_sources_async(query: str):
    """异步并发搜索多个源"""
    tasks = [source.search(query) for source in sources]
    results = await asyncio.gather(*tasks)
    return [r for result_list in results for r in result_list]
```

### 优化2: 结果缓存
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query: str, source_name: str):
    """带缓存的搜索"""
    source = sources[source_name]
    return source.search(query)
```

## Error Handling

### 重试机制
```python
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3))
def search_with_retry(query: str):
    """带重试的搜索"""
    return source.search(query)
```

### 超时控制
```python
def search_with_timeout(query: str, timeout: int = 5):
    """带超时的搜索"""
    try:
        result = source.search(query)
        return result
    except requests.Timeout:
        logger.error(f"Search timeout after {timeout}s")
        return []
```

---

**设计完成时间**: 2025-12-27
**设计师**: Claude Code
**版本**: 1.0
