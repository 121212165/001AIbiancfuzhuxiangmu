# Design - Web UI (Web界面)

## Architecture Overview

### Component Architecture
```
┌──────────────────────────────────────────────┐
│            Streamlit App                      │
│  - frontend/app.py                            │
└────────────────┬─────────────────────────────┘
                 │ HTTP API
┌────────────────▼─────────────────────────────┐
│          FastAPI Backend                     │
│  - /api/v1/nodes                             │
│  - /api/v1/paths                             │
│  - /api/v1/stats                             │
│  - /api/v1/frontier                          │
│  - /api/v1/explore/*                         │
└──────────────────────────────────────────────┘
```

## Layout Design

### 主界面布局
```
┌─────────────────────────────────────────────────────┐
│                    Header                           │
│              🔭 Explorer Agent Dashboard            │
├──────────────┬──────────────────────────────────────┤
│              │                                      │
│  Sidebar     │         Main Content                 │
│  (控制面板)   │                                      │
│              │   ┌────────────────────────────┐    │
│  探索设置    │   │  Tab1: 🆕 最新发现         │    │
│  - 策略      │   │  - 节点列表                 │    │
│  - 迭代次数  │   │  - 评分过滤                 │    │
│  - 启动按钮  │   │  - 详情展开                 │    │
│              │   └────────────────────────────┘    │
│  添加种子    │                                      │
│  - 输入框    │   ┌────────────────────────────┐    │
│  - 优先级    │   │  Tab2: 🛤️ 探索路径         │    │
│  - 添加按钮  │   │  - 路径列表                 │    │
│              │   │  - 价值过滤                 │    │
│  统计信息    │   │  - 节点序列                 │    │
│  - 总节点    │   │  - 继续探索                 │    │
│  - 总路径    │   └────────────────────────────┘    │
│  - 种子数    │                                      │
│  - 平均分    │   ┌────────────────────────────┐    │
│              │   │  Tab3: 📊 质量分析         │    │
│  质量分布    │   │  - 分数分布直方图           │    │
│  - 🌟 高     │   │  - 评分统计                 │    │
│  - ⭐ 中高   │   │  - 系统说明                 │    │
│  - 📉 低     │   └────────────────────────────┘    │
│              │                                      │
│              │   ┌────────────────────────────┐    │
│              │   │  Tab4: 🎯 探索管理         │    │
│              │   │  - 种子池管理               │    │
│              │   │  - 批量操作                 │    │
│              │   │  - 随机种子                 │    │
│              │   └────────────────────────────┘    │
└──────────────┴──────────────────────────────────────┘
```

## Component Design

### 1. API Helper Functions

**职责**: 封装后端API调用，实现缓存

```python
import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"

@st.cache_data(ttl=60)
def fetch_stats():
    """获取系统统计 (缓存60秒)"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/stats")
        return response.json()
    except Exception as e:
        st.error(f"获取统计失败: {e}")
        return {}

@st.cache_data(ttl=60)
def fetch_nodes(limit=50, min_value=0.0):
    """获取节点列表 (支持过滤)"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/nodes?limit={limit}")
        nodes = response.json().get("nodes", [])
        # 客户端过滤
        if min_value > 0:
            nodes = [n for n in nodes if n.get('value_score', 0) >= min_value]
        return nodes
    except Exception as e:
        st.error(f"获取节点失败: {e}")
        return []

@st.cache_data(ttl=60)
def fetch_paths(limit=20, min_value=0.0):
    """获取路径列表 (支持过滤)"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/paths?limit={limit}")
        paths = response.json().get("paths", [])
        if min_value > 0:
            paths = [p for p in paths if p.get('total_value', 0) >= min_value]
        return paths
    except Exception as e:
        st.error(f"获取路径失败: {e}")
        return []

@st.cache_data(ttl=60)
def fetch_frontier():
    """获取种子列表"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/frontier")
        data = response.json()
        return data.get("seeds", [])
    except Exception as e:
        st.error(f"获取种子失败: {e}")
        return []
```

### 2. 探索控制函数

```python
def trigger_exploration(max_iterations=5, strategy="mixed"):
    """触发探索任务"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/explore/start",
            params={"max_iterations": max_iterations, "strategy": strategy}
        )
        return response.json()
    except Exception as e:
        st.error(f"探索失败: {e}")
        return None

def explore_from_path(path_id):
    """从路径继续探索"""
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/explore/from_path/{path_id}")
        return response.json()
    except Exception as e:
        st.error(f"探索失败: {e}")
        return None

def explore_from_seed(seed_id):
    """从种子探索"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/explore/from_seed/{seed_id}",
            params={"max_iterations": 3}
        )
        return response.json()
    except Exception as e:
        st.error(f"探索失败: {e}")
        return None
```

### 3. 种子管理函数

```python
def add_frontier_seed(seed_text, priority=0.5):
    """添加种子"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/frontier/add",
            json={"seed": seed_text, "priority": priority}
        )
        return response.json()
    except Exception as e:
        st.error(f"添加失败: {e}")
        return None

def clear_frontier():
    """清空所有种子"""
    try:
        response = requests.delete(f"{BACKEND_URL}/api/v1/frontier/clear")
        return response.json()
    except Exception as e:
        st.error(f"清空失败: {e}")
        return None
```

### 4. 主UI结构

```python
def main():
    st.title("🔭 Explorer Agent Dashboard")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("控制面板")

        # 探索设置
        st.subheader("探索设置")
        strategy = st.selectbox(
            "探索策略",
            ["mixed", "random", "edge", "graph"],
            help="mixed: 混合 | random: 随机 | edge: 边缘 | graph: 图探索"
        )
        max_iterations = st.slider("迭代次数", 1, 10, 5)

        if st.button("🚀 立即探索", type="primary"):
            with st.spinner("探索中..."):
                result = trigger_exploration(max_iterations, strategy)
                if result:
                    st.success(f"已启动: {result.get('task_id')}")
                    st.cache_data.clear()

        # 统计显示
        stats = fetch_stats()
        st.metric("总节点数", stats.get("total_nodes", 0))
        st.metric("总路径数", stats.get("total_paths", 0))
        st.metric("待探索种子", stats.get("frontier_count", 0))
        st.metric("平均价值分", f"{stats.get('avg_value_score', 0):.2f}")

    # 主内容区 - 标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "🆕 最新发现",
        "🛤️ 探索路径",
        "📊 质量分析",
        "🎯 探索管理"
    ])

    # 每个标签页的内容...
    with tab1:
        # 最新发现内容
        pass

    with tab2:
        # 探索路径内容
        pass

    # ... 其他标签页
```

### 5. 节点列表组件 (Tab 1)

```python
with tab1:
    st.subheader("最新发现")

    # 过滤器
    min_score_filter = st.slider(
        "最低价值分过滤",
        0.0, 1.0, 0.0, 0.1,
        key="node_score_filter"
    )

    nodes = fetch_nodes(100, min_value=min_score_filter)

    if nodes:
        for node in nodes:
            score = node.get('value_score', 0)
            emoji = '🌟' if score >= 0.8 else '⭐' if score >= 0.7 else '📌' if score >= 0.5 else '📄'

            with st.expander(
                f"{emoji} [{score:.2f}] {node.get('title', node.get('content', ''))[:80]}"
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**标题**: {node.get('title', 'N/A')}")
                    st.write(f"**来源**: {node.get('source', 'unknown')}")
                    st.write(f"**类型**: {node.get('type', 'unknown')}")
                with col2:
                    st.write(f"**价值分**: {score:.3f}")
                    st.write(f"**发现时间**: {node.get('discovered_at', 'unknown')}")
                    if node.get('tags'):
                        st.write(f"**标签**: {', '.join(node['tags'])}")

                st.markdown(f"**内容摘要**:\n{node.get('content', '')[:500]}...")
    else:
        st.info("暂无发现，点击左侧按钮开始探索")
```

### 6. 路径列表组件 (Tab 2)

```python
with tab2:
    st.subheader("探索路径")

    min_value_filter = st.slider(
        "路径总价值过滤",
        0.0, 5.0, 0.0, 0.5,
        key="path_value_filter"
    )

    paths = fetch_paths(50, min_value=min_value_filter)

    if paths:
        for path in paths:
            path_value = path.get('total_value', 0)
            nodes_list = path.get('nodes', [])

            with st.expander(
                f"🛤️ 路径 #{path.get('id', '')} "
                f"({'🌟' if path_value >= 2.0 else '⭐' if path_value >= 1.0 else '📊'} "
                f"价值: {path_value:.2f}, 节点: {len(nodes_list)})"
            ):
                # 显示路径节点
                for i, node in enumerate(nodes_list):
                    score = node.get('value_score', 0)
                    emoji = '🌟' if score >= 0.8 else '⭐' if score >= 0.7 else '📌'
                    st.write(f"{emoji} **步骤 {i+1}**: {node.get('title', '')[:80]} ({score:.2f})")

                # 继续探索按钮
                if st.button(f"🔄 沿此路径继续探索", key=f"explore_path_{path.get('id')}"):
                    with st.spinner(f"正在从路径 {path.get('id')} 探索..."):
                        result = explore_from_path(path.get('id'))
                        if result:
                            st.success(f"已启动探索!")
                            st.cache_data.clear()
    else:
        st.info("暂无探索路径")
```

### 7. 质量分析组件 (Tab 3)

```python
with tab3:
    st.subheader("质量评测系统分析")

    all_nodes = fetch_nodes(1000)

    if all_nodes:
        col1, col2 = st.columns(2)

        with col1:
            st.write("**价值分数分布**")
            scores = [n.get('value_score', 0) for n in all_nodes]

            fig = go.Figure(data=[go.Histogram(
                x=scores,
                nbinsx=20,
                marker_color='lightblue',
                name='价值分数'
            )])
            fig.update_layout(
                xaxis_title="价值分数",
                yaxis_title="节点数量",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.write("**评分统计**")
            if scores:
                st.metric("平均分", f"{sum(scores)/len(scores):.3f}")
                st.metric("最高分", f"{max(scores):.3f}")
                st.metric("最低分", f"{min(scores):.3f}")
                st.metric("中位数", f"{sorted(scores)[len(scores)//2]:.3f}")

        # 系统说明
        st.subheader("质量评测系统说明")
        st.write("""
        **当前AI评估器**: 智谱AI GLM-4-Flash

        **评估标准** (0.0-1.0分):
        1. **新颖性** (0-1): 是否提供了新的信息或视角？
        2. **质量** (0-1): 信息是否可信、有深度？
        3. **潜力** (0-1): 是否能启发新的思考或发现？

        **评分等级**:
        - 🌟 **高价值** (≥0.7): 优秀内容，值得深入探索
        - ⭐ **中高价值** (0.5-0.7): 良好内容，有一定价值
        - 📌 **中等价值** (0.3-0.5): 普通内容，可保留
        - 📉 **低价值** (<0.3): 低质量内容，会被过滤
        """)
```

### 8. 种子管理组件 (Tab 4)

```python
with tab4:
    st.subheader("探索管理与种子池")

    frontier = fetch_frontier()

    if frontier:
        st.write(f"**当前种子池**: {len(frontier)} 个待探索种子")

        for seed in frontier:
            s_id, s_text, s_priority, s_attempts = (
                seed.get('id'),
                seed.get('seed'),
                seed.get('priority'),
                seed.get('attempts', 0)
            )

            cols = st.columns([4, 2, 2, 2])
            with cols[0]:
                st.text_input("种子", s_text, key=f"seed_text_{s_id}", disabled=True)
            with cols[1]:
                st.metric("优先级", f"{s_priority:.2f}")
            with cols[2]:
                st.metric("尝试", s_attempts)
            with cols[3]:
                if st.button("🔍 探索", key=f"explore_seed_{s_id}"):
                    with st.spinner(f"正在从 '{s_text}' 探索..."):
                        result = explore_from_seed(s_id)
                        if result:
                            st.success(f"已启动探索!")
                            st.cache_data.clear()
                            st.rerun()

        # 批量操作
        st.markdown("---")
        st.subheader("批量添加种子")

        batch_seeds = st.text_area(
            "每行一个种子（推荐论文主题/关键词）",
            value="quantum machine learning\ntransformer architecture\n...",
            height=200
        )

        if st.button("📥 批量添加"):
            seeds_list = [s.strip() for s in batch_seeds.split('\n') if s.strip()]
            success_count = 0
            for seed in seeds_list:
                result = add_frontier_seed(seed, 0.8)
                if result:
                    success_count += 1
            st.success(f"成功添加 {success_count}/{len(seeds_list)} 个种子")
            st.cache_data.clear()
            st.rerun()

        if st.button("🗑️ 清空所有种子"):
            result = clear_frontier()
            if result:
                st.success(f"已删除 {result.get('deleted_count', 0)} 个种子")
                st.cache_data.clear()
                st.rerun()
```

## Technology Stack

**Frontend Framework**: Streamlit 1.28+
**Visualization**: Plotly 5.0+
**Data Processing**: Pandas 2.0+
**HTTP Client**: Requests 2.31+

## Styling

### Color Scheme
- Primary: `#FF4B4B` (Streamlit Red)
- Secondary: `#FFD700` (Gold - for high value)
- Tertiary: `#C0C0C0` (Silver - for medium value)
- Background: `#FFFFFF` (White)
- Text: `#262730` (Dark Gray)

### Emoji Usage
- 🌟 High value (≥0.8)
- ⭐ Medium-high value (0.7-0.8)
- 📌 Medium value (0.5-0.7)
- 📄 Low value (<0.5)
- 📉 Very low value (<0.3)

### Font Sizes
- Header: 24px
- Subheader: 18px
- Body: 14px
- Small: 12px

---

**设计完成时间**: 2025-12-27
**设计师**: Claude Code
**版本**: 1.0
